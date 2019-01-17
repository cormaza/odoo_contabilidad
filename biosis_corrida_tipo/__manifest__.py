# -*- coding: utf-8 -*-
{
    'name': "biosis_corrida_tipo_cambio",

    'summary': """
       Corrida de tipo de cambio a fin de mes""",

    'description': """
        Ninguna
    """,

    'author': "BIOSIS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_asset','account','biosis_cont'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/view_account_form.xml',
        'views/currency_rate_run_form.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}