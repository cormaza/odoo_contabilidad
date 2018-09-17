# -*- coding: utf-8 -*-
{
    'name': "Facturación electrónica",

    'summary': """
        Módulo que permite realizar facturas que puedan ser emitidas a SUNAT""",

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
                'odoope_toponyms', 'report', 'product', 'sale', 'point_of_sale', 'biosis_cont'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/einvoice.xml',
        'views/producto_product.xml',
        'views/res_partner.xml',
        'views/product_uom_form_view.xml',
        # 'views/sale_make_invoice_advance_views.xml',
        'data/paper_format.xml',
        'reports/report_einvoice_terrestre.xml',
        'reports/report_einvoice_regular.xml',
        'reports/report_einvoice_pos.xml',
        'reports/report_einvoice_ticket.xml',
        # 'data/parameters.xml',
        'data/product_uom.xml',
        'data/einvoice_series.xml',
        'views/point_of_sale.xml',
        #Vistas para poblete
        #'views/invoice_boletas_moras_import.xml',
        #'views/invoice_boletas_moras.xml',

        # 'wizard/contingencia.xml',
        # 'wizard/einvoice_import.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
}
