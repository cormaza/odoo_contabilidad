# -*- coding: utf-8 -*-
{
    'name': "biosis_pagos_masivos",

    'summary': """
       Formulario indexado al registro de pago masivo de moras""",

    'description': """
        Pago de MORAS.
    """,

    'author': "BIOSIS",
    'website': "http://www.biosis.com.pe",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'biosis_pagos_moras', 'biosis_facturacion'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/payments_all_moras.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}