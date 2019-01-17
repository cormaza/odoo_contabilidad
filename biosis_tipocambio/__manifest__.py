# -*- coding: utf-8 -*-
{
    'name': "biosis_tipocambio",

    'summary': """
        Permite obtener el tipo de cambio automaticamente desde SUNAT""",

    'description': """
        Obtención de tipo de cambio para USD
    """,

    'author': "BIOSIS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','biosis_cont'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/cron.xml',
        'data/secuencia_journal.xml',
        'views/res_currency_rate_view.xml',
        'views/account_journal_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}