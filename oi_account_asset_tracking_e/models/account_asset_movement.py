'''
Created on Jul 29, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api,_

class AssetMovement(models.Model):
    _name = 'account.asset.movement'
    _description = 'Asset Movement'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']
    _order = 'date desc,id desc'
    
    name = fields.Char('Number', required = True, readonly = True, default= lambda self: _('New'))
    date = fields.Date(required = True, default = fields.Date.today)
    asset_id = fields.Many2one('account.asset', required = True, index = True)
    description = fields.Text()
    
    location_id = fields.Many2one('account.asset.location', required = True)
    employee_id = fields.Many2one('hr.employee')
    department_id = fields.Many2one('hr.department')
    
    current_location_id = fields.Many2one('account.asset.location', string='Current Location', compute = '_calc_current', store = True)
    current_employee_id = fields.Many2one('hr.employee', string='Current Employee', compute = '_calc_current', store = True)
    current_department_id = fields.Many2one('hr.department', string='Current Department', compute = '_calc_current', store = True)
    
        
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(self._name)            
        return super(AssetMovement, self).create(vals_list)        
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.department_id = self.employee_id.department_id
        
    @api.depends('asset_id')
    def _calc_current(self):
        for record in self:
            for fname in ['location_id', 'employee_id', 'department_id']:
                record['current_%s' % fname] = record.asset_id[fname]
    

    
    def _on_approve(self):
        super(AssetMovement, self)._on_approve()
        if self.location_id.account_asset_use_state_id:
            self.asset_id.use_state_id = self.location_id.account_asset_use_state_id.id
        elif self.asset_id.use_state_id == self.env.ref('oi_account_asset_use_state.use_state_new', False) and self.env.ref('oi_account_asset_use_state.use_state_active', False):
            self.asset_id.use_state_id = self.env.ref('oi_account_asset_use_state.use_state_active', False)
                        