# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        if len(self.invoice_ids) == 0:
            return
        if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
            if self.invoice_ids.is_liquidacion == True:
                self.payment_difference = self.amount - self.invoice_ids.saldo
            else:
                self.payment_difference = self.amount - self._compute_total_invoices_amount()
        else:
            self.payment_difference = self._compute_total_invoices_amount() - self.amount

        if self.pago_detraccion == True:
            value = self.invoice_ids.monto_detraccion_soles
            self.control_detraccion = value - self.amount

    @api.multi
    def post(self):
        if self.invoice_ids.is_liquidacion==True:
            self.pagos_multiples()
        else:
            super(AccountPayment, self).post()
            if self.impuesto == True:
                if self.journal_id.type == 'bank':
                    if self.payment_type == 'outbound':
                        if self.has_invoices == False:
                            account_move = self.env['account.move']
                            for rec in self:
                                ctx = dict(self._context, lang=rec.partner_id.lang)

                                date_payment = fields.Date.context_today(self)
                                company_currency = rec.company_id.currency_id

                                pml = rec.itf_line_move_get(rec, company_currency)
                                part = self.env['res.partner']._find_accounting_partner(rec.partner_id)
                                line = [(0, 0, self.env['account.invoice'].line_get_convert(l, part.id)) for l in pml]

                                # 1er Asiento
                                line1 = []
                                line1.append(line[0])
                                line1.append(line[1])
                                # 2do Asiento
                                line2 = []
                                line2.append(line[2])
                                line2.append(line[3])

                                journal = rec.journal_id.with_context(ctx)
                                date = date_payment
                                move_vals_1 = {
                                    'line_ids': line1,
                                    'journal_id': journal.id,
                                    'date': date,
                                }

                                move_vals_2 = {
                                    'line_ids': line2,
                                    'journal_id': journal.id,
                                    'date': date,
                                }

                                ctx['company_id'] = rec.company_id.id
                                ctx_nolang = ctx.copy()
                                ctx_nolang.pop('lang', None)

                                move1 = account_move.with_context(ctx_nolang).create(move_vals_1)
                                move1.post()

                                move2 = account_move.with_context(ctx_nolang).create(move_vals_2)
                                move2.post()
                            return True

    @api.multi
    def pagos_multiples(self):
        liquidacion = self.invoice_ids
        for linea in self.invoice_ids.invoice_line_ids:
            self.invoice_ids = {}
            self.invoice_ids = linea.factura_relacionada
            self.invoice_ids.origin = linea.invoice_id.order_liquidacion
            self.partner_id = linea.factura_relacionada.partner_id
            self.amount = linea.factura_relacionada.amount_total
            self.state = 'draft'
            self.post_pagos()

        liquidacion.state = 'paid'
        self.invoice_ids.state = 'paid'
        liquidacion.residual = 0


    def post_pagos(self):
        for rec in self:

            if rec.state != 'draft':
                raise UserError(
                    _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                sequence_code)
            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(
                    lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})

