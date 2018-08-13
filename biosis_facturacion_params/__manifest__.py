# -*- coding: utf-8 -*-
{
    'name': "BIOSIS Facturación - parametros",

    'summary': """
        Parametros de configuracion generales para facturación electrónica""",

    'description': """
        Long description of module's purpose
    """,

    'author': "BIOSIS",
    'website': "http://www.biosis.com.pe",

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
        'data/signer.xml',
    ],
}