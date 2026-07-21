'''
Created on Nov 5, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    business_trip_id = fields.Many2one('business.trip', string='Business Trip', readonly = True, index = True)