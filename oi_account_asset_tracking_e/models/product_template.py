'''
Created on Jul 31, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    asset_ids = fields.One2many('account.asset', 'product_tmpl_id')
    asset_count = fields.Integer(compute = '_calc_asset_count', string='Asset Count')

    @api.depends('asset_ids')
    def _calc_asset_count(self):
        for record in self:
            record.asset_count = len(record.asset_ids)
    
    def action_view_assets(self):
        action, =self.env.ref('oi_account_asset_tracking_e.act_asset_tracking').read()
        action['domain'] = [('product_tmpl_id','=', self.id)]
        action['context'] = {
                'default_product_id' : self.product_variant_id.id
            }
        return action