# -*- coding: utf-8 -*-
{
    'name': "biosis_letras",

    'summary': """
       Módulo de Letras a cobrar""",

    'description': """
        Nota: Las facturas ligadas a una letra seran procesadas a pago único.
    """,

    'author': "BIOSIS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'biosis_cont'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/journal.xml',
        'views/account_journal_view.xml',
        'views/account_letra.xml',
        'views/account_letra_pago.xml',
        # 'views/warning_banco.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
