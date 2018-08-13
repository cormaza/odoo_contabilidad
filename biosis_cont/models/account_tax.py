# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    destiny_account_id = fields.Many2one('account.account',string=u'Cuenta de destino')
    codigo_percepcion = fields.Char(string=u'Código percepción')
    codigo_catalogo5 = fields.Char(string=u'Código')
    tax_type_catalogo5 = fields.Char(string=u'Tipo')
    monto_minimo_impuesto_renta = fields.Float(string='Monto minimo a aplicar')