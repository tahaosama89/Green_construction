'''
Created on Jan 3, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
from odoo.tools.safe_eval import test_python_expr
from odoo.exceptions import ValidationError

class BusinessTripALWConfig(models.Model):
    _name='business.trip.alw.config'
    _description ='business.trip.alw.config'
    _order = 'name'

    DEFAULT_PYTHON_CODE = """# result = record.total_days * 100 """

    name = fields.Char(required = True)
    title = fields.Char(required = True)
    active = fields.Boolean(default = True)
    product_id = fields.Many2one('product.product', string='Product', required = True, domain = [('can_be_expensed', '=', True)])
    code = fields.Text('Python Code', default=DEFAULT_PYTHON_CODE)
        
    _sql_constraints= [
            ('name_unqiue', 'unique(name)', 'Name must be unique!')
        ]    
    
    @api.onchange('name')
    def _onchange_name(self):
        self.title = self.name
        
    
    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault('name', _("%s (copy)") % (self.name or ''))
        return super(BusinessTripALWConfig, self).copy(default)        
        
    @api.constrains('code')
    def _check_code(self):
        for record in self:
            if record.code:
                msg = test_python_expr(expr=record.code.strip(), mode="exec")
                if msg:
                    raise ValidationError(msg)
    