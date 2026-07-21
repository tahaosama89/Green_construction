# -*- coding: utf-8 -*-
{
    'name': 'Workflow Engine Base',
    'summary': 'Configurable Workflow Engine, Workflow, Workflow Engine, Approval, Approval '
               'Engine, Approval Process, Escalation, Multi Level Approval',
    'version': '17.0.1.6.6',
    'category': 'Extra Tools',
    'website': 'https://www.open-inside.com',
    'description': '''
    		Configurable Workflow Engine
    		 
        ''',
    'images': ['static/description/cover.png'],
    'author': 'Openinside',
    'license': 'OPL-1',
    'price': 400.0,
    'currency': 'USD',
    'installable': True,
    'depends': ['mail',
                 'oi_base',
                 'web',
                 'base_automation',
                 'oi_fields_selection',
                 'oi_web_selection_field_dynamic'
                 ],
    'data': ['security/ir.model.access.csv',
              'data/ir_sequence.xml',
              'view/approval_config.xml',
              'view/approval_approve_wizard.xml',
              'view/approval_reject_wizard.xml',
              'view/approval_forward_wizard.xml',
              'view/approval_return_wizard.xml',
              'view/approval_transfer_wizard.xml',
              'view/approval_cancel_wizard.xml',
              'view/approval_escalation.xml',
              'view/approval_state_update.xml',
              'view/approval_settings.xml',
              'view/cancellation_record_view.xml',
              'view/action.xml',
              'view/menu.xml',
              'view/templates.xml',
              'data/mail_activity_type.xml',
              'view/res_config_settings.xml',
              'data/ir_cron.xml'],
    'assets': {'web.assets_backend': [
            'oi_workflow/static/src/js/*.js',
            'oi_workflow/static/src/xml/*.xml'
        ],
                },
    'odoo-apps': True,
    'application': False
}