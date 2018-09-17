# -*- coding: utf-8 -*-
{
    'name': u"SBC - Cotización y Logística",

    'summary': u"""
        Módulo a medida para el proceso de cotización de SBC""",

    'description': u"""
        Módulo que permite agregar las siguientes características:
        
        - Datos de líneas navieras
        - Datos de tipos de contenedores
        - Ayuda al momento de generar una cotización para el cliente
    """,

    'author': "ALTA BPO",
    'website': "http://altabpo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','biosis_common',],

    # always loaded
    'data': [
        'views/views.xml',
        'views/linea_naviera.xml',
        'views/product_template.xml',
        'views/tipo_contenedor.xml',
        'views/sale_quest_view.xml',
        'data/data_inicial.xml',
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'reports/layout.xml',
        'reports/sale_order_contrato.xml',
        'data/email_template_sbc_cotizacion.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}