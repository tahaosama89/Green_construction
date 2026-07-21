'''
Created on Apr 10, 2022

@author: Zuhair Hammadi
'''
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    business_trip_journal_id = fields.Many2one('account.journal', domain=[('type', '=', 'purchase')])
    bt_has_days_limit = fields.Boolean()
    bt_days_limit = fields.Float()
    bt_set_eligibility = fields.Boolean() 
    bt_eligible_after = fields.Float()
    bt_approval_expense_id = fields.Many2one('approval.config', domain=[('model', '=', 'business.trip' )])