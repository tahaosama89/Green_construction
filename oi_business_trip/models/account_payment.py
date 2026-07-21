'''
Created on Nov 6, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class Payment(models.Model):
    _inherit = 'account.payment'
    
    business_trip_id = fields.Many2one('business.trip', string='Business Trip', readonly = True, index = True)