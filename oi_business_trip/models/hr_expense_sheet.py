'''
Created on Nov 6, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields,_
from odoo.exceptions import UserError

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    business_trip_id = fields.Many2one(related='expense_line_ids.business_trip_id')
    
    def _check_can_approve(self):
        if self.user_has_groups('oi_business_trip.group_business_trip_officer') and self.business_trip_id:
            pass
        else:    
            super(HrExpenseSheet, self)._check_can_approve()