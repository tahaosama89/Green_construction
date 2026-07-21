'''
Created on Aug 25, 2020

@author: Fatima Shubbar
'''
from odoo import models, fields
class Wizard(models.TransientModel):
    _name = 'account.asset.dispose.wizard'
    _description = "Asset Disposal Wizard"
    
    new_use_state = fields.Many2one('account.asset.use.state', ondelete='set null',
                                     string="Status", index=True) 
    reason = fields.Text(string="Dispose Reason")
        
    def process(self):
        record_id = self._context.get('active_id')
        record = self.env['account.asset'].browse(record_id)
        record.write({'use_state_id':self.new_use_state.id, 'dispose_reason': self.reason})
        return record.set_to_close()