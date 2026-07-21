# -*- coding: utf-8 -*-
{
    'name': 'Assets Tracking (Enterprise)',
    'summary': 'Asset, Assets, Asset Management, Assets Management, Asset Tracking, Track, '
    'Trace, Trace Asset',
    'description': '''
        Assets Tracking Enterprise
    ''',
    'author': 'Openinside',
    'website': 'https://www.open-inside.com',
    'license': 'OPL-1',
    'category': 'Accounting',
    'version': '17.0.0.0.1',
    'depends': ['account_asset', 'oi_workflow', 'hr', 'purchase_stock'],
    'data': ['security/res_groups.xml',
             'security/ir.model.access.csv',
             'data/ir_sequence.xml',
             'view/account_asset_asset.xml',
             'view/account_asset_attribute.xml',
             'view/account_asset_location.xml',
             'view/account_asset_movement.xml',
             'view/account_asset_dispose_wizard.xml',
             'view/account_asset_use_state.xml',
             'view/hr_employee.xml',
             'view/hr_employee.xml',
             'view/product_template.xml',
             'view/stock_warehouse.xml',
             'view/action.xml',
             'view/menu.xml'],
    'application': True,
    'installable': True,
    'price': 129.99,
    'odoo-apps': True,
    'images': [],
    'currency': 'USD'
}
