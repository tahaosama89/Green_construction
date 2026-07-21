'''
Created on Nov 5, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, time, timedelta
import pytz

class BusinessTripMixin(models.AbstractModel):
    _name='business.trip.mixin'
    _description = 'Business Trip Mixin'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']
    _order ='name desc'
    
    @api.model
    def _country_domain(self):
        if self.env['res.country.group'].search([('business_trip','=', True)], limit = 1):
            return [('country_group_ids.business_trip', '=', True)]
        return []
    
    @api.model
    def default_service(self):
        return self.env['business.trip.service'].search([('default','=', True)])   
    
    name = fields.Char('Number', required = True, readonly = True, default = lambda self : _('New'), copy = False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)    
    currency_id = fields.Many2one(related='company_id.currency_id', readonly = True)    
    employee_id = fields.Many2one('hr.employee', string='Employee', required = True, default=lambda self: self.env.user.employee_ids[:1])
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True, readonly=True)
    
    department_id = fields.Many2one('hr.department', string='Department', compute = '_calc_employee_related', store = True, change_default=True)
    job_id = fields.Many2one('hr.job', string='Job Position', compute = '_calc_employee_related', store = True, change_default=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', compute = '_calc_employee_related', store = True)
    
    date_from = fields.Date('Start Date', required = True, tracking = True)
    date_to = fields.Date('End Date', required = True, tracking = True)
    number_of_days = fields.Integer('Number of Days', store=True, tracking = True)
    extra_days = fields.Integer("Extra Days", compute='_calc_extra_days', store=True, tracking = True)
    total_days = fields.Integer("Total Days", compute='_calc_total_days', store=True, tracking = True)    
    
    country_id = fields.Many2one('res.country', string="Country", required=True, domain = _country_domain, tracking = True, change_default=True)
    country_code = fields.Char(related='country_id.code', readonly = True)
    country_group_id = fields.Many2one('res.country.group', string='Country Group', compute = '_calc_country_group_id', store = True, tracking = True, change_default=True)
    country_group_name = fields.Char(related='country_group_id.name', readonly = True)
    country_enforce_cities = fields.Boolean(related='country_id.enforce_cities', readonly=True)
    city_id = fields.Many2one('res.city', string='City', tracking = True)    
    city = fields.Char('City Name', tracking = True)
    
    from_country_id = fields.Many2one('res.country', string="From Country", domain = _country_domain)
    from_city_id = fields.Many2one('res.city', string='From City')   
    from_city = fields.Char('From City Name')    
       
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    
    expense_ids = fields.One2many('hr.expense', 'business_trip_id', string='Expenses')
    expense_count = fields.Integer(compute = '_calc_expense_count')
    expense_amount = fields.Monetary('Expense Amount', compute = '_calc_expense_amount', compute_sudo = True, store = True)
    
    payment_ids = fields.One2many('account.payment', 'business_trip_id', string='Payments')
    payment_count = fields.Integer(compute = '_calc_payment_count')
    payment_amount = fields.Monetary('Payment Amount', compute = '_calc_payment_amount', compute_sudo = True, store = True)
    
    allowances_ids = fields.One2many('business.trip.alw', 'business_trip_id', string='Allowances')
    allowance_amount = fields.Monetary(compute = '_calc_allowance_amount', string='Allowance Amount', store = True, tracking = True)   
    hide_allowances = fields.Boolean(compute = '_calc_hide_allowances')
    
    ticket_class = fields.Selection([('first','First Class'), ('business','Business Class'), ('economy','Economy Class')], string='Ticket Class', tracking = True)
    ticket_class_id = fields.Many2one('business.trip.ticket.class')
    
    meeting_id = fields.Many2one('calendar.event', string='Meeting', readonly = True)
    
    _Provider_Selection = [('company', 'Company'), ('employee','Employee')]
    
    housing_provider = fields.Selection(_Provider_Selection, 'Housing Provider')
    food_provider = fields.Selection(_Provider_Selection, 'Food Provider')
    ticket_provider = fields.Selection(_Provider_Selection, 'Ticket Provider')
    ticket_amount = fields.Monetary()
    transport_provider = fields.Selection(_Provider_Selection, 'Transportation Provider')
    visa_provider = fields.Selection(_Provider_Selection, 'Visa Provider')
    visa_amount = fields.Monetary()
 
    allowed_employee_ids = fields.Many2many('hr.employee', store = False, compute = '_calc_allowed_employee')

    is_officer = fields.Boolean(compute='_compute_is_officer')
    contract_id = fields.Many2one('hr.contract', compute = '_calc_contract_id', store = True)
    days_consumed_per_year = fields.Float(string="Number of days consumed in year", compute = '_calc_days_consumed_per_year')
    completion_report = fields.Binary()
    file_name = fields.Char()
    advance_payment = fields.Boolean(string="Request Advance Payment", tracking = True)
    
    service_ids = fields.Many2many('business.trip.service', string='Required Services', default=default_service)
    service_codes = fields.Json(compute = "_calc_service_codes")
    
    _sql_constraints= [
        ('name_unqiue', 'unique(company_id, name)', 'Number must be unique!')
        ]     

    @api.depends('service_ids.code')
    def _calc_service_codes(self):
        for record in self:
            record.service_codes = record.mapped("service_ids.code")
                        
    @api.depends_context('uid')
    @api.depends('name')
    def _compute_is_officer(self):
        group = {
            "business.trip" : "oi_business_trip.group_business_trip_officer",
            "hr.training.request" : "oi_hr_training.group_training_officer"
            }.get(self._name)
        is_officer = self.env.user.has_group(group)
        
        for record in self:
            record.is_officer = is_officer
            
    @api.depends('employee_id', 'date_from')
    def _calc_contract_id(self):
        for record in self:
            contract = False
            if record.date_from and record.employee_id:
                for contract in record.sudo().employee_id.contract_ids.sorted('date_start', reverse = True):
                    if  contract.state in ['draft','cancel']:
                        continue
                    if contract.date_start > record.date_from:
                        continue
                    if contract.date_end and contract.date_end < record.date_from:
                        continue
                    break
                                
            record.contract_id = contract    
 
    @api.depends('employee_id', 'date_from')
    def _calc_days_consumed_per_year(self):
        for record in self:
            if not record.date_from:
                record['days_consumed_per_year'] = False
                continue
            year_start = '%s-01-01' % record.date_from.year
            year_end = '%s-12-31' % record.date_from.year
            other_ids = self.env['business.trip'].search([('employee_id','=', record.employee_id.id),('state','not in', ['draft','rejected','canceled']), ('date_from', '>=', year_start), ('date_from', '<=', year_end), ('id','!=', record._origin.id)])
            record['days_consumed_per_year'] = sum(other_ids.mapped('number_of_days'))
  
    @api.depends('country_id', 'city_id')
    def _calc_country_group_id(self):
        for record in self:
                if record.city_id:
                    country_group_id = self.env['res.country.group'].search([('city_ids', '=', record.city_id.id), ('business_trip', '=', True)], limit =1)
                    if country_group_id:
                        record.country_group_id = country_group_id
                        continue
                    
                record.country_group_id = record.country_id.country_group_ids.filtered('business_trip')[:1]
    
    @api.depends('allowances_ids')
    def _calc_hide_allowances(self):        
        hide_allowances = not bool(self.env['business.trip.alw.config'].search([('active','=', True)], limit = 1))
        for record in self:
            record.hide_allowances = hide_allowances
    
    @api.depends('allowances_ids.amount', 'allowances_ids.paid')
    def _calc_allowance_amount(self):
        for record in self:
            record.allowance_amount = sum(record.allowances_ids.filtered('paid').mapped('amount'))
    
    @api.depends('payment_ids')
    def _calc_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)
    
    @api.depends('employee_id')
    def _calc_employee_related(self):
        for record in self:
            record.department_id = record.employee_id.department_id
            record.job_id = record.employee_id.job_id
            record.manager_id = record.employee_id.parent_id
    
    @api.onchange('date_from', 'date_to')
    def _calc_number_of_days(self):
        for record in self:
            if record.date_from and record.date_to:
                record.number_of_days = (fields.Date.from_string(record.date_to) - fields.Date.from_string(record.date_from)).days + 1
            else:
                record.number_of_days = 0
                
    @api.constrains('number_of_days')
    def _check_number_of_days(self):
        for record in self:
            number_of_days = (record.date_to - record.date_from).days + 1
            if record.number_of_days != number_of_days:
                record.number_of_days = number_of_days
    
    @api.depends('country_group_id')
    def _calc_extra_days(self):
        for record in self:
            record.extra_days = record.country_group_id.extra_days
    
    @api.depends('number_of_days', 'extra_days')
    def _calc_total_days(self):
        for record in self:
            record.total_days = record.number_of_days + record.extra_days
                                
    @api.depends('expense_ids.total_amount', 'expense_ids.currency_id','expense_ids.state')
    def _calc_expense_amount(self):
        for record in self:
            total_amount = 0
            for expense in record.expense_ids:
                if expense.state=='refused':
                    continue
                total_amount +=expense.currency_id._convert(expense.total_amount, record.currency_id,record.company_id, expense.date)
            record.expense_amount = total_amount                      
            
    @api.depends('payment_ids.amount', 'payment_ids.currency_id','payment_ids.state')
    def _calc_payment_amount(self):
        for record in self:
            total_amount = 0
            for payment in record.payment_ids:
                if payment.state=='cancelled':
                    continue
                amount =payment.currency_id._convert(payment.amount, record.currency_id, record.company_id, payment.date)
                if payment.payment_type == 'inbound':
                    amount = -amount
                total_amount += amount
            record.payment_amount = total_amount
    
    @api.depends('expense_ids')
    def _calc_expense_count(self):
        for record in self:
            record.expense_count = len(record.expense_ids)
            
    @api.depends('name')  
    def _calc_allowed_employee(self):
        for record in self:
            env = self.env
            employee_ids = env.user.employee_ids
            if 'delegation_ids' in env.user:
                group = {
                    "business.trip" : 'oi_business_trip.group_business_trip_emp',
                    "hr.training.request" : 'oi_hr_training.group_training_emp'
                    }.get(self._name)
                employee_ids += env.user.delegation_ids.filtered(lambda delegation : delegation.group_id == env.ref(group)).mapped('delegator_id')
            record.allowed_employee_ids = employee_ids
                       
    @api.onchange('date_to')
    def _onchange_date_to(self):            
        if self.date_to and self.number_of_days:
            date_from = self.date_to - timedelta(days = self.number_of_days - 1) 
            if self.date_from != date_from:
                self.date_from = date_from            
                
    @api.onchange('number_of_days', 'date_from')
    def _onchange_number_of_days(self):
        if self.number_of_days <=0:
            return
        if self.date_from:
            date_to = self.date_from + timedelta(days = self.number_of_days - 1) 
            if self.date_to != date_to:
                self.date_to = date_to
        elif self.date_to:
            date_from = self.date_to - timedelta(days = self.number_of_days - 1) 
            if self.date_from != date_from:
                self.date_from = date_from
                
    @api.onchange('city_id')
    def _onchange_city_id(self):
        self.city = self.city_id.name                
    
    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_('Start Date > End Date'))
            

    def _on_submit(self):
        date = self.date_from
        if self.employee_id.company_id.bt_set_eligibility and self.employee_id.first_contract_date:
            total_days = (date - self.employee_id.first_contract_date).days + 1
            if total_days < self.employee_id.company_id.bt_eligible_after:
                raise ValidationError(_("You can only request business trips after %s days of starting")%(self.employee_id.company_id.bt_eligible_after))
            
        self.flush_model(['days_consumed_per_year'])
        if self.employee_id.company_id.bt_has_days_limit and (self.days_consumed_per_year + self.number_of_days) > self.employee_id.company_id.bt_days_limit:
            raise ValidationError(_("Your request can not be submitted because you have exceeded the %s days policy")%(self.employee_id.company_id.bt_days_limit))
          
    def _on_approval(self, old_state, new_state):
        if self._name == "business.trip":
            approve_expense = self.company_id.bt_approval_expense_id.state == old_state
        elif self._name == "hr.training.request":
            approve_expense = self.company_id.training_approval_expense_id.state == old_state
            
        if approve_expense:
            self.sudo()._create_calendar_event()
            self.sudo()._create_allowances_expense()
            self.sudo()._approve_allowances_expense()
            self.sudo()._create_resource_leave()
                  
    def _on_approve(self):
        super(BusinessTripMixin, self)._on_approve()
        self.sudo()._create_calendar_event()
        self.sudo()._create_allowances_expense()
        self.sudo()._approve_allowances_expense()
        self.sudo()._create_resource_leave()
            
    def _on_reject(self):
        super(BusinessTripMixin, self)._on_reject()
        self._remove_calendar_event()      
        self._remove_resource_leave()
        
        if self.sudo().expense_ids.filtered(lambda expense : expense.state == 'done'):
            raise UserError('You cannot reject a record with Paid Expenses')
        else:
            if self.expense_ids.business_trip_id:
                expense_sheets = self.env['hr.expense.sheet'].sudo().search([('business_trip_id','=',self.id),('state','!=','cancel')])
            elif self.expense_ids.training_request_id:
                expense_sheets = self.env['hr.expense.sheet'].sudo().search([('training_request_id','=',self.id),('state','!=','cancel')])
            else:
                expense_sheets = False 
            if expense_sheets:
                expense_sheets.account_move_ids.button_cancel()
                self.sudo().expense_ids.write({'state' : 'refused'})
                self._remove_resource_leave()
                self._remove_calendar_event()
                self.sudo().allowances_ids.write({'expense_id' : False})
                         
    def _prepare_meeting_values(self):
        self.ensure_one()
        
        categ_id = {
            "business.trip" : "oi_business_trip.event_type_business_trip",
            "hr.training.request" : "oi_hr_training.event_type_training"            
            }.get(self._name)
        
        meeting_values = {
            'name': self.get_description(),
            'categ_ids': self.env.ref(categ_id, False),
            'description': self.details,
            'user_id': self.user_id,
            'start': fields.Datetime.to_datetime(self.date_from),
            'stop': fields.Datetime.to_datetime(self.date_to),
            'allday': True,
            'state': 'open',  # to block that meeting date in the calendar
            'privacy': 'confidential',
            'partner_ids' : self.user_id.partner_id,
            'res_id' : self.id,
            'res_model_id' : self.env['ir.model']._get_id(self._name),
            'location' : ' - '.join(filter(None, [self.country_id.name, self.city])),
            'activity_ids' : [(5,)]
        }
        return self.env['calendar.event']._convert_to_write(meeting_values)
            
    
    def _create_calendar_event(self):
        for record in self:                   
            if not record.meeting_id:                 
                record.meeting_id=self.env['calendar.event'].create(record._prepare_meeting_values())
        return True            
    
    def _remove_calendar_event(self):
        return self.mapped('meeting_id').unlink()        
    
    def action_expense(self):
        column = self.get_link_column()
        self.ensure_one()
        action, = self.sudo().env.ref('hr_expense.hr_expense_actions_my_all').read()
        action['name'] = 'Expenses'
        action['display_name'] = 'Expenses'
        action['domain'] = [(column,'=', self.id)]
        action['context'] = {
            f'default_{column}' : self.id,
            'default_analytic_account_id' : self.analytic_account_id.id,
            'default_employee_id' : self.employee_id.id,
            'default_date' : self.date_from
            }
        return action
    
    
    def action_payment(self):
        column = self.get_link_column()
        payment_employee = self.env['ir.module.module'].search([('name','=', 'oi_account_payment_employee'), ('state','=', 'installed')])
        
        self.ensure_one()
        if payment_employee:
            action, = self.env.ref('oi_account_payment_employee.action_account_payments_employee').read()
        else:
            action, = self.env.ref('account.action_account_payments_payable').read()
        action['domain'] = [(column,'=', self.id)]
        context = safe_eval(action.get('context') or '{}')
        context.update({
            f'default_{column}' : self.id,
            'default_partner_id' : self.employee_id.work_contact_id.id,    
            'default_communication' : 'Business Trip %s' % self.get_description(),
            'default_amount' : self.expense_amount - self.payment_amount
            })
        if payment_employee:
            context.update({
                'default_partner_type': 'employee',
                'search_default_employee_filter': 1,
                'default_is_employee_payment': True,
                })
            action['view_id'] = self.env.ref('oi_account_payment_employee.view_account_employee_payment_tree').id
        action['context'] = context
        
        return action
    
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code(self._name)
        return super(BusinessTripMixin, self).create(vals_list)
    
    
    def unlink(self):
        if any(self.filtered(lambda record : record.state!='draft')):
            raise UserError(_('You can delete draft status only'))
        self._remove_calendar_event()
        self._remove_resource_leave()
        return super(BusinessTripMixin, self).unlink()                   
    
    @api.onchange('employee_id', 'date_from', 'date_to', 'country_id', 'city', 'total_days')
    def compute_allowances(self):
        for record in self:
            record._calc_contract_id()
            for f in ['employee_id', 'date_from', 'date_to', 'country_id']:
                if not record[f]:
                    return
            if record.state==record._get_approved_state():
                continue
            column = self.get_link_column()      
                                
            for config in self.env['business.trip.alw.config'].search([]):
                localdict = record._get_eval_context()
                
                def log(message, level="info"):
                    with self.pool.cursor() as cr:
                        cr.execute("""
                            INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                            VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (self.env.uid, 'server', self._cr.dbname, __name__, level, message, self._name, config.id, config.name))
                
                localdict['log'] = log                                                
                
                safe_eval(config.code, localdict, mode='exec', nocopy=True)
                amount = localdict.get('result') or 0
                alw_id = record.allowances_ids.filtered(lambda al : al.config_id == config)
                if alw_id:
                    if alw_id.amount != amount:
                        alw_id.amount = amount 
                else:
                    if amount:
                        vals = {
                            column : record.id,
                            'config_id' : config.id,
                            'amount' : amount,
                            'paid' : True
                            }
                        if isinstance(record.id, models.NewId):
                            record.allowances_ids += self.env['business.trip.alw'].new(vals)
                        else:
                            self.env['business.trip.alw'].create(vals)
    
    @api.onchange('employee_id', 'service_ids')         
    def _onchange_ticket_class(self):
        ticket_class_id = False
        if self.employee_id and 'ticket' in self.service_codes:  
            for ticket in self.env['business.trip.ticket.class'].search([]):
                if ticket.force_domain and self.sudo().filtered_domain(safe_eval(ticket.force_domain)):
                    ticket_class_id = ticket.id
                    break
        self.ticket_class_id = ticket_class_id  

    @api.onchange('housing_provider', 'ticket_provider','ticket_amount','visa_provider','visa_amount')         
    def _onchange_test(self):
        self.compute_allowances()
        
        
                      
    def _create_allowances_expense(self):
        for alw in self.mapped('allowances_ids'):
            if alw.expense_id or not alw.paid or not alw.amount:
                continue
            column = self.get_link_column()                 
            expense_id = self.env['hr.expense'].sudo().create({
                column : alw[column].id,
                'analytic_distribution' : {alw[column].analytic_account_id.id: 100} if alw[column].analytic_account_id else None,
                'employee_id' : alw[column].employee_id.id,
                'date' : fields.Date.today(),
                'price_unit' : alw.amount,
                'product_id' : alw.config_id.product_id.id,
                'name' : '%s - %s' % (alw[column].get_description(), alw.name),
                'total_amount': alw.amount
                })
            expense_id._compute_tax_ids()
            expense_id._compute_account_id()
            expense_id.price_unit = alw.amount
            alw.expense_id = expense_id
            
             
    def _approve_allowances_expense(self):
        self = self.with_context(approval_no_mail = True)
        for record in self:
            expense_ids = [record.mapped('allowances_ids.expense_id').filtered(lambda expense : expense.state=='draft')]
            
            if self.env['ir.config_parameter'].sudo().get_param('hr.expense.no_multiple') == 'True':
                expense_ids=expense_ids[0]
            for expense_id in expense_ids:
                if not expense_id:
                    continue
                expense_id = expense_id.sudo()
                
                if expense_id.sheet_id:
                    sheet_id = expense_id.sheet_id
                else:
                    sheet_id = self.env['hr.expense.sheet'].create(expense_id._get_default_expense_sheet_values())
                    journal_id_field = {
                        "business.trip" : "business_trip_journal_id",
                        "hr.training.request" : "training_journal_id"
                        }.get(self._name)                    
                    
                    if record.company_id[journal_id_field]:
                        sheet_id.journal_id = record.company_id[journal_id_field].id
                                        
                    sheet_id.update({
                        'expense_line_ids' : [(6,0, expense_id.ids)]                    
                        })
                
                if sheet_id.state in ['draft', 'submit']:
                    sheet_id.sudo()._do_approve()
                    sheet_id.sudo().action_sheet_move_create()                                                  
            
    @api.model
    def to_naive_utc(self, datetime):
        tz_name = self._context.get('tz') or self.env.user.tz
        tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
        return tz.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(pytz.UTC)
            
    def _create_resource_leave(self):
        self._remove_resource_leave()
        column = self.get_link_column()                  
        
        for record in self:
            extra_days = timedelta(days=int(record.extra_days / 2))
            date_from = self.to_naive_utc(datetime.combine(record.date_from, time.min)) - extra_days
            date_to = self.to_naive_utc(datetime.combine(record.date_to, time.max)) + extra_days
            self.env['resource.calendar.leaves'].create({
                'name': record.name,
                'date_from': date_from.strftime('%Y-%m-%d %H:%M:%S'),
                column: record.id,
                'date_to': date_to.strftime('%Y-%m-%d %H:%M:%S'),
                'resource_id': record.employee_id.resource_id.id,
                'calendar_id': record.employee_id.resource_calendar_id.id,
                'time_type' : 'leave'
            })
        return True
    
    def _remove_resource_leave(self):
        return self.env['resource.calendar.leaves'].search([(self.get_link_column(), 'in', self.ids)]).unlink()
        
    
    @api.model
    def get_link_column(self):
        return {
            "business.trip" : "business_trip_id",
            "hr.training.request" : "training_request_id"
            }.get(self._name)
                        
    def get_description(self):
        self.ensure_one()
        return f"{self.env['ir.model']._get(self._name).name} {self.name}"
    
    @api.constrains('date_from', 'date_to','state')
    def _check_period_overlap(self):
        ignored_states = ['draft','rejected','canceled']
        for record in self:
            if record.state in ignored_states:
                continue
            duplicate_bt = self.search([('id','!=',record.id),('employee_id','=',record.employee_id.id),('date_from','<=',record.date_to),('date_to','>=',record.date_from),('state','not in',ignored_states)])
            if duplicate_bt:
                msg = {
                    "business.trip" : _('Current Period overlaps with other Business Trip Period.'),
                    "hr.training.request" : _('Current Period overlaps with other Training Period.')                    
                    }.get(self._name)
                raise ValidationError(msg)
    