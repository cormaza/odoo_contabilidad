# -*- coding: utf-8 -*-
{
    'name': "cont_report",

    'summary': """
        Reporte de liquidación y facturación ... 
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','biosis_common','report_xlsx'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/report_liquidacion_wizard.xml',
        # 'views/report_liquidacionpago.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}