'''
Created on Oct 23, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AccountAssetUseState(models.Model):
    _name = 'account.asset.use.state'
    _description = _name
    _order= 'sequence,id'
    
    name = fields.Char(required = True, translate = True)
    value = fields.Char(required = True)
    dispose = fields.Boolean()
    sequence = fields.Integer()    
    
    _sql_constraints= [
            ('name_unqiue', 'unique(name)', 'Name must be unique!'),
            ('value_unqiue', 'unique(value)', 'Value must be unique!')
        ]    
    
 