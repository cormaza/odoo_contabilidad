# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountMasivosDetraccion(models.Model):
    _name = 'payment.purchase.liquidacion'
    _description = 'Pago Masivo Liquidacion y Facturas de Proveedor'
    _rec_name = 'number'
    _order = "id desc"

    @api.multi
    def get_comprobantes(self):
        in_invoice = self.env['account.invoice'].search([('type', '=', 'in_invoice'), ('state', '=', 'open')])
        a = 1

    number = fields.Char(String=u'Número de Documento' , default=get_comprobantes)
    referencia = fields.Char(String=u'Referencia')
    invoice_id = fields.Char(String=u'Número de Documento')
    cliente = fields.Many2one('res.partner', string='Proveedor')
    ole_oli = fields.Char(String=u'OLE/OLI')
    fecha_emision = fields.Date(string=u'Fecha de Emisión', index=True)
    fecha_vencimiento = fields.Date(string=u'Fecha de Vencimiento', index=True)
    dias_credito = fields.Char(string=u'Días Crédito', index=True)
    fecha_corte = fields.Date(string=u'Fecha de Corte', index=True)
    fecha_pago = fields.Date(string=u'Fecha de Pago', index=True)
    currency_id = fields.Many2one('res.currency', string='Moneda')
    monto_total = fields.Monetary(string='Total')
















