# -*- coding: utf-8 -*-
{
    'name': "Biosis Contabilidad - Liquidaciones",

    'summary': """
        Módulo para crear liquidaciones para proveedores""",

    'description': """
        Este módulo permite crear liquidaciones en base a las facturas de compras realizadas para un cliente en particular
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','biosis_cont','biosis_facturacion'],

    # always loaded
    'data': [

        'data/journal.xml',
        'views/account_liquidacion_view.xml',
        'views/account_invoice_supplier_form.xml',
        'views/account_invoice_view.xml',
        'views/payment_purchase_liquidacion.xml',
        'views/payments_all.xml',
        #'wizard/payment_purchase_liquidacion.xml',
        #'views/payment_purchase_liquidacion.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}