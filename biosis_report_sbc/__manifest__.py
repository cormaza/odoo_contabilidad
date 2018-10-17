# -*- coding: utf-8 -*-
{
    'name': "biosis_report_sbc",

    'summary': """
        Reportes sobre facturas de clientes, liquidaciones de cobranza y facturas de compra""",

    'description': """
        Long description of module's purpose
    """,

    'author': "BIOSIS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'wizard/report_liquidacioncompra.xml',
        'wizard/report_ventas.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}