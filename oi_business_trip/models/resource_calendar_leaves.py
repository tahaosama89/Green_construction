'''
Created on May 1, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class CalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    business_trip_id = fields.Many2one("business.trip", string='Business Trip', readonly = True)
