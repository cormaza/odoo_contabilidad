# -*- coding: utf-8 -*-
{
    'name': "biosis_suscripcion",

    'summary': """
        Manejo de mora en por suscripcion""",

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
    'depends': ['base','sale_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/auto.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/sale_suscripcion_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}