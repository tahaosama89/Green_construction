'''
Created on Nov 5, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class BusinessTrip(models.Model):
    _name='business.trip'
    _description = 'Business Trip'
    _inherit = ['business.trip.mixin']
    _order ='name desc'

    
    title = fields.Char('Trip Title', required=True)
    details = fields.Text('Trip Details')
    comments = fields.Text()    
               
    _sql_constraints= [
        ('name_unqiue', 'unique(company_id, name)', 'Number must be unique!')
        ]     
    
