'''
Created on Jan 3, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields
from odoo.tools.sql import column_exists

class BusinessTripALW(models.Model):
    _name='business.trip.alw'
    _description ='business.trip.alw'
    
    business_trip_id = fields.Many2one('business.trip', required = True, ondelete='cascade') 
    config_id = fields.Many2one('business.trip.alw.config', required = True)
    name = fields.Char(related='config_id.title', readonly = True)
    amount = fields.Float()
    
    paid = fields.Boolean('Paid to Employee', default = True)
    
    expense_id = fields.Many2one('hr.expense', readonly = True)
        
    _sql_constraints= [
            ('alw_unqiue', 'unique(business_trip_id, config_id)', 'Allowance must be unique!')
        ]
    
    
    def _auto_init(self):
        super()._auto_init()
        cr = self.env.cr
        if column_exists(cr, "product_template", "sale_line_warn"):
            cr.execute("ALTER TABLE product_template  ALTER COLUMN sale_line_warn SET DEFAULT 'no-message';")