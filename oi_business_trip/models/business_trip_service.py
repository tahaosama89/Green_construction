'''
Created on Nov 5, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class BusinessTripService(models.Model):
    _name='business.trip.service'
    _description='business.trip.service'
    _order = 'sequence,id'

    name = fields.Char(required = True, translate = True)    
    code = fields.Char(required = True) 
    active = fields.Boolean(default = True)
    default = fields.Boolean()
    business_trip = fields.Boolean(default = True)
    sequence = fields.Integer()
    
    _sql_constraints= [
            ('name_unqiue', 'unique(name)', 'Name must be unique!')
        ]