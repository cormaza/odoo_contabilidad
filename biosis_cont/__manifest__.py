# -*- coding: utf-8 -*-
{
    'name': "Biosis Contable",

    'summary': """
        Permite manejar la contabilidad de tu empresa o de varias empresas  """,

    'description': """
        Contabilidad para Perú
    """,

    'author': "Biosis",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_asset', 'purchase', 'l10n_es_account_asset','l10n_pe'],

    # always loaded
    'data': [
        'data/journal.xml',
        'data/account_data.xml',
        'data/anexo3_tablas.xml',
        'data/anexo4_detraccion.xml',
        'views/templates.xml',
        'views/account_payment_view.xml',
        'views/product_template_view.xml',
        'views/account_config_settings_view.xml',
        'views/account_journal_view.xml',
        'views/account_tax_view.xml',
        'views/account_asset_category_form.xml',
        'views/account_invoice_supplier_form.xml',
        'views/views.xml',
        'views/account_invoice_view.xml',
        'views/account_move_view.xml',
        'views/account_gastos_bancarios.xml',
        'views/account_payment_invoice_form.xml',
        'views/account_analytic.account.xml',
        'views/recibos_honorarios.xml',
        'views/account_bank_statement.xml',
        'views/res_currency_rate_view.xml',
        'views/account_move_view.xml',
        'views/account_anexo4_detraccion.xml',
        #'views/res_partner.xml',
        #'views/account_payment_detraccion.xml',

        #'views/account_invoice_import_txt.xml',
        #'views/hr_expense_view.xml',
        #'views/sale_order_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}