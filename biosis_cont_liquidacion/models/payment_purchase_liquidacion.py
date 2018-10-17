# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPurchaseLiquidacion(models.Model):
    _inherit = 'account.invoice'

    fecha_recepcion = fields.Date(string=u'Fecha de Recepción', index=True)
    fecha_corte = fields.Date(string=u'Fecha de Corte', index=True)
    fecha_pago = fields.Date(string=u'Fecha de Pago', index=True)


class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.model
    def default_get(self, fields):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        invoices = self.env[active_model].browse(active_ids)
        amount = 0
        sw = 0
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("Las facturas deben tener la misma moneda!."))

        for factura in invoices:
            id = factura.id
            fact = self.env['account.invoice'].search([('id', '=', id)], limit=1)
            if fact.type == 'in_invoice':
                amount = amount + fact.amount_total
                pass
            else:
                sw = 1
        if sw == 1:
            super(account_register_payments, self).default_get(fields)
        else:
            data = {
                'amount': abs(amount),
                'currency_id': invoices[0].currency_id.id,
                'payment_type': amount > 0 and 'inbound' or 'outbound',
                'partner_id': invoices[0].commercial_partner_id.id,
                'partner_type': 'customer',
                'communication': "Pago masivo",
            }
            return data

    def post_pagos_liquidacion_facturas(self, factura):

        for factura_id in factura['active_ids']:
            invoice = self.env['account.invoice'].search([('id', '=', factura_id)], limit=1)
            # self.post_pagos_moras(invoice_mora)
            data = {
                'payment_type': 'outbound',
                'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                'partner_type': 'supplier',
                'partner_id': invoice.partner_id.id,
                'amount': invoice.amount_total,
                'payment_difference': 0,
                'currency_id': self.currency_id.id,
                'payment_date': self.payment_date,
                'journal_id': self.journal_id.id,
                'state': 'draft',
                'name': self.communication
            }
            payment = self.env['account.payment'].create(data)
            payment.invoice_ids = invoice
            payment.post()
