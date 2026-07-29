# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConstructionMaterialRequestLine(models.Model):
    _name = 'construction.material.request.line'
    _description = 'Construction Material Request Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Seq.', default=10)

    request_id = fields.Many2one(
        'construction.material.request',
        string='Material Request',
        required=True,
        ondelete='cascade',
        index=True,
    )

    # ─── Product ──────────────────────────────────────────────────────────────

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('purchase_ok', '=', True)],
    )
    description = fields.Char(string='Description')
    qty = fields.Float(string='Quantity', default=1.0, required=True)
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    unit_cost = fields.Float(string='Unit Cost')
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
    )

    # ─── Requisition type ─────────────────────────────────────────────────────

    request_type = fields.Selection(
        selection=[
            ('purchase', 'Purchase Order'),
            ('internal', 'Internal Picking'),
        ],
        string='Requisition Action',
        default='purchase',
        required=True,
    )

    # ─── Vendor (for purchase lines) ─────────────────────────────────────────

    partner_ids = fields.Many2many(
        'res.partner',
        'construction_material_request_line_partner_rel',
        'line_id',
        'partner_id',
        string='Vendor(s)',
        domain=[('supplier_rank', '>', 0)],
    )

    # ─── WBS link (optional) ─────────────────────────────────────────────────

    wbs_id = fields.Many2one(
        'project.wbs',
        string='WBS',
        related='request_id.wbs_id',
        store=True,
        readonly=True,
    )

    # ─── Remarks ─────────────────────────────────────────────────────────────

    notes = fields.Text(string='Notes')

    # ─── Computed ─────────────────────────────────────────────────────────────

    @api.depends('qty', 'unit_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.qty * rec.unit_cost

    # ─── Onchange ─────────────────────────────────────────────────────────────

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.description_purchase or self.product_id.name
            self.uom_id = self.product_id.uom_po_id or self.product_id.uom_id
            self.unit_cost = self.product_id.standard_price
