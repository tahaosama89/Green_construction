'''
Created on Oct 17, 2021

@author: Jaber Ali
'''
from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    asset_location_id = fields.Many2one('account.asset.location',string='Asset Location')
        