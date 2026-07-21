'''
Created on Jul 29, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'
    
    asset_ids = fields.One2many('account.asset', 'employee_id')    