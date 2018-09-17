# -*- coding: utf-8 -*-
import datetime
import calendar
from odoo import api, fields, models, _

class AccountLiquidacionLine(models.Model):
    _name = 'account.liquidacion.line'
    _description = u'Lina de Pago - Liquidación'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    currency_id = fields.Many2one('res.currency', string='Moneda')
    liquidacion_id = fields.Many2one('account.liquidacion',string='Liquidación', required=True)
    amount_total = fields.Monetary(string='Monto detracción')
    concepto_pago = fields.Char(string='Concepto del Pago')
    invoice_id = fields.Many2one('account.invoice', string='Factura relacionada')

    @api.multi
    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        if self.invoice_id:
            self.amount_total = self.invoice_id.amount_total

