'''
Created on Jul 29, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class AssetLocation(models.Model):
    _name = 'account.asset.location'
    _description = 'Asset Location'
    
    name = fields.Char(required = True)
    active = fields.Boolean(default=True)
    code = fields.Char()
    warehouse = fields.Boolean()
    scrap = fields.Boolean()
    account_asset_use_state_id = fields.Many2one('account.asset.use.state',string='Asset State')
    
    asset_ids = fields.One2many('account.asset', 'location_id')
    asset_count = fields.Integer(compute = '_calc_asset_count', string='Asset Count')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    @api.depends('asset_ids')
    def _calc_asset_count(self):
        for record in self:
            record.asset_count = len(record.asset_ids)
    
    def action_asset(self):
        action, = self.env.ref("oi_account_asset_tracking_e.act_asset_tracking").read()
        action['domain'] = [('location_id','=', self.id)]
        return action
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        domain = args or []
        domain += [
            '|',
            ('name', operator, name),
            ('code', operator, name),
        ]
        return self.search(domain, limit=limit).name_get()
    