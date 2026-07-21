'''
Created on Dec 26, 2023

@author: Elyas
'''
from odoo import models, fields

class EmployeeServices(models.Model):
    _name = 'business.trip.ticket.class'
    _description = 'Business Trip Ticket Class'
    
    name = fields.Char(required = True)
    code = fields.Char()
    model_id = fields.Many2one('ir.model', required = True, ondelete = 'cascade', readonly = True,
                                default = lambda self: self.env['ir.model'].search([('model','=','business.trip')]))
    model_name = fields.Char(related = 'model_id.model')
    active = fields.Boolean(default = True)
    force_domain = fields.Char()