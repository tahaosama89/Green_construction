'''
Created on May 22, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class ChangeDocumentStatus(models.TransientModel):
    _name = 'approval.state.update'
    _description = 'Change Document Status'
        
    state = fields.Char(required = True, string='Status')
    res_model = fields.Char(required = True)
    res_ids = fields.Json(required = True)
        
    def action_update(self):        
        records = self.env[self.res_model].browse(self.res_ids)
        records.write({"state" : self.state})
        return {'type': 'ir.actions.act_window_close'}