'''
Created on Jul 29, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class Department(models.Model):
    _inherit = 'hr.department'
    
    asset_ids = fields.One2many('account.asset', 'department_id')    