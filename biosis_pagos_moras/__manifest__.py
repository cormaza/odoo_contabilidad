# -*- coding: utf-8 -*-
{
    'name': "biosis_pagos_moras",

    'summary': """
       Permite importar archivo txt con el fin de conciliar los comprobantes generados
       con los datos importados""",

    'description': """
        Conciliación de cobros de alquileres
    """,

    'author': "BIOSIS",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'contacts', 'odoope_ruc_validation', 'odoope_einvoice_base',
                'odoope_toponyms', 'product', 'sale', 'biosis_facturacion'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'views/invoice_boletas_moras.xml',
        'views/invoice_payment_all.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}