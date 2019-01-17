# -*- coding: utf-8 -*-
{
    'name': "biosis_account_move",

    'summary': """
      Lectura de libro diario en excel para la importacion de asientos contables""",

    'description': """
        Asientos contables masivos
    """,

    'author': "BIOSIS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'wizard/account_move_import.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}