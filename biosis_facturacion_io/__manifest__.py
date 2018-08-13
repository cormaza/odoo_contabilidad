# -*- coding: utf-8 -*-
{
    'name': "Facturación electrónica I/E",

    'summary': """
        Módulo que permite importr y exportar comprobantes que puedan ser emitidas a SUNAT""",

    'description': """
        Este módulo permite:
        - Generar documentos electrónicos
        - Firmar documentos electrónicos
        - Emitir documentos electrónicos
        - Mostrar página web de consulta de comprobantes electrónicos
    """,

    'author': "BIOSIS",
    'website': "http://www.biosis.com.pe",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Invoicing &amp; Payments',
    'version': '0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'contacts', 'mail', 'odoope_ruc_validation', 'odoope_einvoice_base',
                'odoope_toponyms', 'report','product', 'biosis_facturacion'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/contingencia.xml',
        'wizard/einvoice_import.xml',
        'wizard/regenerar_xml.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
