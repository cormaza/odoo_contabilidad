# # -*- coding: utf-8 -*-
# from StringIO import StringIO
# from odoo.exceptions import UserError, ValidationError
# from datetime import datetime, date
# from odoo import api, fields, models, _
# import base64
# MAP_INVOICE_TYPE_PARTNER_TYPE = {
#     'out_invoice': 'customer',
#     'out_refund': 'customer',
#     'in_invoice': 'supplier',
#     'in_refund': 'supplier',
# }
#
# MAP_INVOICE_TYPE_PAYMENT_SIGN = {
#     'out_invoice': 1,
#     'in_refund': 1,
#     'in_invoice': -1,
#     'out_refund': -1,
# }
#
# class account_register_payments(models.TransientModel):
#     _inherit = "account.register.payments"
#
#     @api.model
#     def default_get(self, fields):
#         context = dict(self._context or {})
#         active_model = context.get('active_model')
#         active_ids = context.get('active_ids')
#         invoices = self.env[active_model].browse(active_ids)
#         amount = 0
#         sw = 0
#         #Primero valido si una de las facturas es MORA, tengo que RESTRINGIR que solo esten afectas a DETRACCION
#         for factura in invoices:
#             id = factura.id
#             fact_detraccion = self.env['account.invoice'].search([('id', '=', id)], limit=1)
#             if fact_detraccion.residual_detraccion_soles > 0 and fact_detraccion.statte == 'open':
#                 amount = amount + fact_detraccion.residual_detraccion_soles
#                 pass
#             else:
#                 sw = 1
#         if sw == 1:
#             super(account_register_payments, self).default_get(fields)
#         else:
#             data = {
#                 'amount': abs(amount),
#                 'currency_id': self.env['res.currency'].search([('name', '=', 'PEN')]).id,
#                 'payment_type': amount > 0 and 'inbound' or 'outbound',
#                 'partner_id': invoices[0].commercial_partner_id.id,
#                 'partner_type': 'customer',
#                 'communication': "",
#             }
#             return data
#
#
#
#     def post_pagos_moras(self,factura_mora):
#
#         for factura_mora_id in factura_mora['active_ids']:
#             invoice_mora = self.env['account.invoice'].search([('id', '=', factura_mora_id)], limit=1)
#             #self.post_pagos_moras(invoice_mora)
#             data = {
#                 'payment_type': 'inbound',
#                 'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
#                 'partner_type': 'customer',
#                 'partner_id': invoice_mora.partner_id.id,
#                 'amount': invoice_mora.amount_total,
#                 'payment_difference': 0,
#                 'currency_id': self.env['res.currency'].search([('name', '=', 'PEN')]).id,
#                 'payment_date': invoice_mora.date_invoice,
#                 'journal_id': self.env['account.journal'].search([('code', '=', 'BNK1')], limit=1).id,
#                 'state': 'draft',
#                 'name': u'Efecto de Pago de MORA por importación de TXT '
#             }
#             # payment = self.env['account.payment'].create(data)
#             # payment.invoice_ids = invoice_mora
#             # payment.post()
#
#
#
#
#
#
