{
    "name": "Business Trip",
    "summary": "Business Trip Management, Employee Travel, Travel, Travel Expense, Employee Travel, Expense, Travel Management, Business Trip",    
    'category': 'Human Resources',
    "description": """
        
         
    """,
    
    "author": "Openinside",
    "license": "OPL-1",
    'website': "https://www.open-inside.com",
    "version": "17.0.2.2.3",
    "price" : 99.99,
    "currency": 'USD',
    "installable": True,
    "depends": [
        'hr_expense', 'calendar', 'oi_workflow', 'base_address_extended', 'account', 'hr_contract'
    ],
    "data": [
        'security/groups.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/business_trip_ticket_class.xml',
        'data/approval_config.xml',
        'data/business_trip_service.xml',
        'data/ir_sequence.xml',
        'data/calendar_event_type.xml',
        'data/products.xml',
        'data/allowances.xml',
        'view/business_trip_ticket_class.xml',
        'view/account_payment.xml',
        'view/business_trip_service.xml',
        'view/business_trip.xml',
        'view/hr_expense_sheet.xml',
        'view/hr_expense.xml',
        'view/business_trip_alw_config.xml',
        'view/res_country_group.xml',
        'view/resource_calendar_leaves.xml',
        'report/business_trip_decision.xml',
        'view/action.xml',
        'view/menu.xml',
        'view/res_config_settings.xml',
    ],
    'images': [
        'static/description/cover.png'
    ],
    'external_dependencies' : {
        
    },  
    "post_init_hook" : "post_init_hook",  
    "uninstall_hook" : "uninstall_hook",
    'odoo-apps' : True      
}

