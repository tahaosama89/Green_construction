'''
Created on Apr 10, 2022

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import odoo

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    business_trip_journal_id = fields.Many2one(related='company_id.business_trip_journal_id', readonly=False, domain="[('company_id', '=', company_id), ('type', '=', 'purchase')]")
    bt_approval_expense_id = fields.Many2one(related='company_id.bt_approval_expense_id', readonly=False, domain="[('model', '=', 'business.trip' )]",name='name')
    hide_bt_analytic_account_id = fields.Boolean(string='Hide Analytic Account Field', store=True)
    bt_has_days_limit = fields.Boolean(related='company_id.bt_has_days_limit', readonly=False)
    bt_days_limit = fields.Float(related='company_id.bt_days_limit', readonly=False)
    bt_set_eligibility = fields.Boolean(related='company_id.bt_set_eligibility', readonly=False) 
    bt_eligible_after = fields.Float(related='company_id.bt_eligible_after', readonly=False)
    hide_bt_completion_report = fields.Boolean(string='Hide Completion Report Field')
    hide_bt_advance_payment = fields.Boolean(string='Hide Advance Payment Field')
    module_oi_business_trip_exceptions = fields.Boolean(string='Business Trip Exceptions')

    bt_expense_salary_rule = fields.Boolean()
    
    def _get_bt_custom_views_fields(self):
        return {
            'hide_bt_analytic_account_id' : ['view_hide_bt_analytic_account_id'],
            'hide_bt_completion_report' : ['view_hide_bt_completion_report'],
            'hide_bt_advance_payment' : ['view_hide_bt_advance_payment']
            }
    
    
    def _get_bt_expense_salary_rules(self):
        if 'hr.salary.rule' not in self.env or 'hr.expense.sheet' not in self.env:
            return
        if not self.env['ir.module.module'].search([('name','=like','oi_payroll_expenses%'),('state','=','installed')]):
            return
        return self.env['hr.salary.rule'].search([('code','=', 'BTEXP')])
    
    
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        for field_name, view_xml_ids in self._get_bt_custom_views_fields().items():
            active = True
            for view_xml_id in view_xml_ids:
                active = active and self.env.ref(f"oi_business_trip.{view_xml_id}").active
            res[field_name] = active
            
        res['bt_expense_salary_rule'] = bool(self._get_bt_expense_salary_rules())
        
        
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for field_name, view_xml_ids in self._get_bt_custom_views_fields().items():
            for view_xml_id in view_xml_ids:
                self.env.ref(f"oi_business_trip.{view_xml_id}").active = self[field_name]
                
        is_enterprise = odoo.release.version.split("-")[0][-1] == 'e'
                
        if self.bt_expense_salary_rule:
            if 'hr.salary.rule' not in self.env:
                raise UserError(_('You need to install Payroll module'))
            if not self.env['ir.module.module'].search([('name','=like','oi_payroll_expenses%'),('state','=','installed')]):
                raise UserError(_('You need to install Payroll Expenses module'))

        
            
            if not self._get_bt_expense_salary_rules():
                category = self.env.ref('oi_payroll.ALW', False) or self.env.ref('hr_payroll.ALW', False)
                vals = {                        
                        'name' : 'Business Trip Expense',
                        'code': 'BTEXP',
                        'category_id' : category.id ,
                        'condition_select' : 'python',
                        'condition_python': """
account_id = employee.work_contact_id.property_account_payable_id.id
expense_sheet_ids = employee.env['hr.expense.sheet']
sheet_ids = employee.env['hr.expense.sheet'].search([('employee_id','=', employee.id),
  ('payment_state','in', ['not_paid','partial']),
  ('state','in', ['post','done']),
  ('business_trip_id','!=', False),('business_trip_id.date_from','<=',payslip.date_to),('business_trip_id.advance_payment','=',False),
  '|', ('slip_line_id','=', False), ('slip_line_id.slip_id','=', payslip.id)])

sheet_ids |= employee.env['hr.expense.sheet'].search([('employee_id','=', employee.id),
  ('payment_state','in', ['not_paid','partial']),
  ('state','in', ['post','done']),
  ('business_trip_id','!=', False),('business_trip_id.date_from','<=',payslip.date_to + relativedelta(months=+1)),('business_trip_id.advance_payment','=',True),
  '|', ('slip_line_id','=', False), ('slip_line_id.slip_id','=', payslip.id)])
  
expense_to_pay = sum(sheet_ids.mapped('account_move_id.amount_residual_signed')) *-1
  
result = bool(expense_to_pay) """,
                        'amount_select' : 'code',
                        'amount_python_compute' : """
result = expense_to_pay
expense_sheet_ids |= sheet_ids
"""
                     }         
                if 'struct_id' in self.env['hr.salary.rule']:                
                    for struct_id in self.env['hr.payroll.structure'].search([]):
                        vals['struct_id'] = struct_id.id
                        self.env['hr.salary.rule'].sudo().create(vals)
                else:
                    vals['struct_ids'] = [(6,0, self.env.ref("oi_payroll.structure_base").ids)]
                    self.env['hr.salary.rule'].sudo().create(vals)
                    


    @api.onchange('module_oi_business_trip_exceptions')
    def _onchange_bt_model(self):
        for name in ['module_oi_business_trip_exceptions']:
            module_name = name[7:]
            if self[name]:
                if not self.env["ir.module.module"].get_module_info(module_name):
                    self[name] = False
                    return {
                        'warning' : {
                            'title' : 'Module not found',
                            'message' : """Module (%s) is not available in your system
Please download it from                            
https://apps.odoo.com/apps/17.0/%s/""" % (module_name,module_name)
                            }
                        }                                   
            