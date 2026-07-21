'''
Created on Jul 29, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Asset(models.Model):
    _inherit = 'account.asset'

    entry_count = fields.Integer(
        compute='_entry_count', string='# Asset Entries')
    code = fields.Char(string='Reference', size=32, readonly=True)
    value = fields.Float(string='Gross Value',
                         required=True, readonly=True, digits=0)
    note = fields.Text()

    date = fields.Date(string='Date', required=True, readonly=True,
                       default=fields.Date.context_today)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', readonly=True)

    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    product_id = fields.Many2one('product.product')
    dispose_reason = fields.Text()

    movement_ids = fields.One2many('account.asset.movement', 'asset_id', domain=[
                                   ('state', '=', 'approved')])
    movement_count = fields.Integer(compute='_calc_movement_count')

    movement_id = fields.Many2one('account.asset.movement', string='Last Movement', compute='_calc_current', store=True,
                                  compute_sudo=True)
    location_id = fields.Many2one(
        'account.asset.location', compute='_calc_current', store=True, compute_sudo=True)
    employee_id = fields.Many2one(
        'hr.employee', compute='_calc_current', store=True, compute_sudo=True)
    department_id = fields.Many2one(
        'hr.department', compute='_calc_current', store=True, compute_sudo=True)

    product_tmpl_id = fields.Many2one(
        related='product_id.product_tmpl_id', store=True)

    image_1920 = fields.Image(related='product_id.image_1920', readonly=True)
    image_1024 = fields.Image(related='product_id.image_1024', readonly=True)
    image_512 = fields.Image(related='product_id.image_512', readonly=True)
    image_256 = fields.Image(related='product_id.image_256', readonly=True)
    image_128 = fields.Image(related='product_id.image_128', readonly=True)

    @api.model
    def _get_use_state_id(self):
        return self.env['account.asset.use.state'].search([], limit=1)

    @api.model
    def get_use_state_value(self):
        return [(state.value, state.name) for state in self.env['account.asset.use.state'].search([])]

    use_state_id = fields.Many2one('account.asset.use.state',
                                   string='Use Status',
                                   default=_get_use_state_id,
                                   copy=False,
                                   tracking=True)

    use_state_value = fields.Selection(
        get_use_state_value, compute='_calc_use_state_value')

    @api.depends('use_state_id.value')
    def _calc_use_state_value(self):
        for record in self:
            record.use_state_value = record.use_state_id.value

    def write(self, vals):
        if 'use_state_id' in vals:
            for record in self:
                if record.state == 'close':
                    raise UserError(_('Asset Closed'))
        return super(Asset, self).write(vals)

    @api.depends('movement_ids.state')
    def _calc_current(self):
        for record in self:
            last_movement = record.movement_ids[:1]
            if last_movement:
                for fname in ['location_id', 'employee_id', 'department_id']:
                    record[fname] = last_movement[fname]
                record.movement_id = last_movement
            else:
                for fname in ['location_id', 'employee_id', 'department_id', 'movement_id']:
                    record[fname] = False

    @api.depends('movement_ids')
    def _calc_movement_count(self):
        for record in self:
            record.movement_count = len(record.movement_ids)

    def action_movement(self):
        action, = self.env.ref(
            'oi_account_asset_tracking_e.act_asset_movement').read()
        action['domain'] = [('asset_id', '=', self.id)]
        action['context'] = {'default_asset_id': self.id}
        return action

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        if self.env["ir.sequence"].search([("code", "=", self._name)]):
            for vals in vals_list:
                if not vals.get("code"):
                    vals["code"] = self.env["ir.sequence"].next_by_code(
                        self._name)
        return super(Asset, self).create(vals_list)
