# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ConstructionMaterialRequest(models.Model):
    _name = 'construction.material.request'
    _description = 'Construction Material Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'
    _rec_name = 'name'

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise UserError(
                    _('You cannot delete a Material Request that is not in Draft, Cancelled, or Rejected state.')
                )
        return super().unlink()

    # ─── Basic Info ───────────────────────────────────────────────────────────

    name = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        default='New',
        index=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('dept_approve', 'Department Approval'),
            ('approve', 'Approved'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('reject', 'Rejected'),
        ],
        default='draft',
        tracking=True,
        string='Status',
    )
    request_date = fields.Date(
        string='Request Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        tracking=True,
    )
    required_date = fields.Date(
        string='Required By',
        tracking=True,
    )
    reason = fields.Text(string='Reason / Justification')

    # ─── Construction Links ───────────────────────────────────────────────────

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        tracking=True,
    )
    contract_id = fields.Many2one(
        'owner.contract',
        string='Contract',
        domain="[('project_id', '=', project_id)]",
        tracking=True,
    )
    wbs_id = fields.Many2one(
        'project.wbs',
        string='WBS',
        domain="[('project_id', '=', project_id)]",
        tracking=True,
    )

    # ─── HR ───────────────────────────────────────────────────────────────────

    employee_id = fields.Many2one(
        'hr.employee',
        string='Requested By',
        default=lambda self: self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1
        ),
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Currency',
        readonly=True,
        store=True,
    )

    # ─── Approvals ────────────────────────────────────────────────────────────

    confirmed_by_id = fields.Many2one(
        'hr.employee', string='Confirmed by', readonly=True, copy=False,
    )
    confirm_date = fields.Date(string='Confirmed Date', readonly=True, copy=False)

    dept_approved_by_id = fields.Many2one(
        'hr.employee', string='Dept. Approved by', readonly=True, copy=False,
    )
    dept_approve_date = fields.Date(string='Dept. Approval Date', readonly=True, copy=False)

    approved_by_id = fields.Many2one(
        'hr.employee', string='Approved by', readonly=True, copy=False,
    )
    approve_date = fields.Date(string='Approval Date', readonly=True, copy=False)

    rejected_by_id = fields.Many2one(
        'hr.employee', string='Rejected by', readonly=True, copy=False,
    )
    reject_date = fields.Date(string='Rejected Date', readonly=True, copy=False)
    reject_reason = fields.Text(string='Rejection Reason', readonly=True, copy=False)

    done_date = fields.Date(string='Completed Date', readonly=True, copy=False)

    # ─── Picking / PO details ─────────────────────────────────────────────────

    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        copy=True,
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,
    )

    # ─── Lines ────────────────────────────────────────────────────────────────

    line_ids = fields.One2many(
        'construction.material.request.line',
        'request_id',
        string='Material Lines',
        copy=True,
    )

    # ─── Computed ─────────────────────────────────────────────────────────────

    total_cost = fields.Float(
        string='Total Estimated Cost',
        compute='_compute_total_cost',
        store=True,
    )
    purchase_order_count = fields.Integer(
        string='Purchase Orders',
        compute='_compute_po_count',
    )
    picking_count = fields.Integer(
        string='Internal Pickings',
        compute='_compute_picking_count',
    )

    # ─── Compute methods ──────────────────────────────────────────────────────

    @api.depends('line_ids.total_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.line_ids.mapped('total_cost'))

    def _compute_po_count(self):
        for rec in self:
            rec.purchase_order_count = self.env['purchase.order'].search_count(
                [('construction_request_id', '=', rec.id)]
            )

    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = self.env['stock.picking'].search_count(
                [('construction_request_id', '=', rec.id)]
            )

    # ─── Onchange ─────────────────────────────────────────────────────────────

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.contract_id = False
        self.wbs_id = False

    # ─── Create (sequence) ────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'construction.material.request'
                ) or 'New'
        return super().create(vals_list)

    # ─── State transitions ────────────────────────────────────────────────────

    def action_confirm(self):
        """Move to Confirmed state."""
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Please add at least one material line before confirming.'))
            rec.confirmed_by_id = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1
            )
            rec.confirm_date = fields.Date.today()
            rec.state = 'confirm'

    def action_dept_approve(self):
        """Department Manager approval."""
        for rec in self:
            rec.dept_approved_by_id = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1
            )
            rec.dept_approve_date = fields.Date.today()
            rec.state = 'dept_approve'

    def action_approve(self):
        """Final procurement/manager approval."""
        for rec in self:
            rec.approved_by_id = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1
            )
            rec.approve_date = fields.Date.today()
            rec.state = 'approve'

    def action_reject(self):
        """Reject the request."""
        for rec in self:
            rec.rejected_by_id = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1
            )
            rec.reject_date = fields.Date.today()
            rec.state = 'reject'

    def action_cancel(self):
        """Cancel the request."""
        for rec in self:
            rec.state = 'cancel'

    def action_reset_draft(self):
        """Reset to Draft."""
        for rec in self:
            rec.state = 'draft'

    def action_done(self):
        """Mark as Done."""
        for rec in self:
            rec.done_date = fields.Date.today()
            rec.state = 'done'

    # ─── Generate PO / Picking ────────────────────────────────────────────────

    def action_create_orders(self):
        """
        Process each approved line:
          - 'purchase' lines → create/extend Purchase Orders grouped by vendor
          - 'internal' lines → create one Internal Picking
        """
        self.ensure_one()
        if self.state != 'approve':
            raise UserError(_('You can only generate orders for Approved requests.'))
        if not self.line_ids:
            raise UserError(_('No material lines to process.'))

        purchase_lines = self.line_ids.filtered(lambda l: l.request_type == 'purchase')
        internal_lines = self.line_ids.filtered(lambda l: l.request_type == 'internal')

        # ── Purchase Orders ──────────────────────────────────
        if purchase_lines:
            po_obj = self.env['purchase.order']
            pol_obj = self.env['purchase.order.line']
            po_dict = {}  # partner → purchase.order record

            for line in purchase_lines:
                if not line.partner_ids:
                    raise UserError(
                        _('Line "%s" has no vendor set. Please set a vendor for purchase lines.')
                        % line.product_id.display_name
                    )
                for partner in line.partner_ids:
                    if partner not in po_dict:
                        po = po_obj.create({
                            'partner_id': partner.id,
                            'currency_id': self.company_id.currency_id.id,
                            'date_order': fields.Date.today(),
                            'company_id': self.company_id.id,
                            'construction_request_id': self.id,
                            'origin': self.name,
                        })
                        po_dict[partner] = po
                    else:
                        po = po_dict[partner]

                    seller = line.product_id._select_seller(
                        partner_id=partner,
                        quantity=line.qty,
                        date=fields.Date.today(),
                        uom_id=line.uom_id,
                    )
                    pol_obj.create({
                        'product_id': line.product_id.id,
                        'name': line.product_id.display_name,
                        'product_qty': line.qty,
                        'product_uom': line.uom_id.id,
                        'date_planned': self.required_date or fields.Date.today(),
                        'price_unit': seller.price if seller else line.unit_cost,
                        'order_id': po.id,
                    })

        # ── Internal Picking ─────────────────────────────────
        if internal_lines:
            if not self.location_id:
                raise UserError(_('Please set a Source Location for internal picking lines.'))
            if not self.dest_location_id:
                raise UserError(_('Please set a Destination Location for internal picking lines.'))
            if not self.picking_type_id:
                raise UserError(_('Please set a Picking Type for internal picking lines.'))

            picking = self.env['stock.picking'].create({
                'partner_id': self.employee_id.user_partner_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.dest_location_id.id,
                'picking_type_id': self.picking_type_id.id,
                'note': self.reason,
                'construction_request_id': self.id,
                'origin': self.name,
                'company_id': self.company_id.id,
            })
            for line in internal_lines:
                self.env['stock.move'].create({
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                    'product_uom': line.uom_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.dest_location_id.id,
                    'name': line.product_id.display_name,
                    'picking_type_id': self.picking_type_id.id,
                    'picking_id': picking.id,
                    'company_id': self.company_id.id,
                })

    # ─── Smart-button actions ─────────────────────────────────────────────────

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        action['domain'] = [('construction_request_id', '=', self.id)]
        action['context'] = {'default_construction_request_id': self.id}
        return action

    def action_view_pickings(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        action['domain'] = [('construction_request_id', '=', self.id)]
        return action
