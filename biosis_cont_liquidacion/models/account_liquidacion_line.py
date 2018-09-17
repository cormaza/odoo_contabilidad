# -*- coding: utf-8 -*-
import datetime
import calendar
from odoo import api, fields, models, _

class AccountLiquidacionLine(models.Model):
    _inherit = 'account.invoice.line'
    _description = u'Lina de Pago - Liquidación'

    fecha_emision = fields.Date(string=u'Fecha Emisión')
    emisor = fields.Char(string=u'Emisor')
    factura_relacionada = fields.Many2one('account.invoice', string='Factura relacionada')

    @api.multi
    @api.onchange('factura_relacionada')
    def onchange_factura_relacionada(self):
        if len(self.factura_relacionada.invoice_line_ids) > 1:
            self.name = 'Liquidacion cobranza'
        else:
            self.name = self.factura_relacionada.invoice_line_ids.product_id.name
        self.emisor = self.factura_relacionada.partner_id.name
        self.fecha_emision = self.factura_relacionada.date_invoice
        self.price_unit = self.factura_relacionada.amount_total
        self.account_id = self.factura_relacionada.account_id


