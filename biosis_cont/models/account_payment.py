# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

TIPO_RESIDUAL = (
    ('f', 'Factura'),
    ('d', 'Detraccion')
)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tipo_documento_pago_id = fields.Many2one('biosis.report.ple.anexo3.tabla1', string=u'Tipo medio pago')
    codigo_referencia_doc = fields.Char(string=u'Código/Referencia')

    impuesto = fields.Boolean(string=u'Operación')
    type_journal = fields.Selection(related='journal_id.type', string=u'Tipo Diario')

    #RENDICION DE CUENTAS
    trabajador = fields.Boolean(string=u'Transf. a trabajador')
    lista_trabajador = fields.Many2one('hr.employee',string=u'Trabajador')
    motivo = fields.Char(string=u'Motivo')


    #tipo_impuesto = fields.Many2one('account.tax', string=u'Descripción tipo operación', domain=[('type_tax_use', '=', 'none')])
    tipo_impuesto = fields.Many2one('account.gastos_bancarios', string=u'Tipo de  operación')

    tipo_residual = fields.Selection(TIPO_RESIDUAL, string='Pago de ', default='f')#campo nuevo

    aplica_detraccion = fields.Boolean(string=u'Aplica detraccion',default=False)

    residual_detraccion = fields.Monetary(related='invoice_ids.residual_detraccion_soles',
                                          string='Residual detraccion')
    pago_detraccion = fields.Boolean(string=u'Pago detracción', readonly=True)

    control_detraccion = fields.Float(string='control det.')


    #payment_type = fields.Selection(selection_add=[('impuestos', 'Entrada de Impuestos')])

    #amount_detraccion = fields.Monetary(string='Cantidad a pagar Detracción')
    #diferencia_pago_detraccion = fields.Monetary(compute='_compute_diferencia_pago_detraccion',string=u'Diferencia pago detracción'
                                                 #,readonly=True)

    # def _compute_total_invoices_amount(self):
    #     """ Compute the sum of the residual of invoices, expressed in the payment currency """
    #     payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or self.env.user.company_id.currency_id
    #     invoices = self._get_invoices()
    #
    #     if all(inv.currency_id == payment_currency for inv in invoices):
    #         if self.aplica_detraccion == False:
    #             total = sum(invoices.mapped('residual_signed'))
    #         else:
    #             if self.tipo_residual == 'f':
    #                 total = sum(invoices.mapped('residual_factura'))
    #                 #Tener en cuenta en caso no haya nada mas que pagar.
    #             else:
    #                 total = sum(invoices.mapped('residual_detraccion'))
    #     else:
    #         total = 0
    #         for inv in invoices:
    #             if self.aplica_detraccion == False:
    #                 if inv.company_currency_id != payment_currency:
    #                     total += inv.company_currency_id.with_context(date=self.payment_date).compute(
    #                         inv.residual_company_signed, payment_currency)
    #                 else:
    #                     total += inv.residual_company_signed
    #             else:
    #                 if self.tipo_residual == 'f':
    #                     total = sum(invoices.mapped('residual_factura_soles'))
    #                     # Tener en cuenta en caso no haya nada mas que pagar.
    #                 else:
    #                     total = sum(invoices.mapped('residual_detraccion_soles'))
    #
    #     return abs(total)

    @api.multi
    def post(self):
        """
        Se extiende el metodo post() de account_payment, el cual contendra la logic para crear el asiento contable donde
        se incluya el ITF.
        """
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
    def post_transfer(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
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
            # cambios implementados
            # if rec.payment_type != 'transfer':

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.journal_id.type == 'bank':
                if rec.payment_type == 'transfer':
                    if rec.impuesto == True:
                        transfer_debit_aml = rec._create_transfer_itf(amount)
                    else:
                        transfer_debit_aml =  rec._create_transfer_entry_transfer(amount)
                else:
                    transfer_debit_aml = rec._create_transfer_entry_transfer(amount)
            else:
                if rec.payment_type == 'transfer':
                    transfer_debit_aml = rec._create_transfer_entry_transfer(amount)



            rec.state = 'posted'

    def _create_transfer_entry_transfer(self, amount):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconciliable move line
        """
        cuenta_efectivo = self.env['account.account'].search([('code', '=like', '101001%')], limit=1)
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, dummy = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
            amount, self.currency_id, self.company_id.currency_id)
        amount_currency = self.destination_journal_id.currency_id and self.currency_id.with_context(
            date=self.payment_date).compute(amount, self.destination_journal_id.currency_id) or 0

        dst_move = self.env['account.move'].create(self._get_move_vals(self.destination_journal_id))

        dst_liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, dst_move.id)
        dst_liquidity_aml_dict.update({
            'name': _('Transfer from %s') % self.journal_id.name,
            'account_id': self.destination_journal_id.default_credit_account_id.id,
            'currency_id': self.destination_journal_id.currency_id.id,
            'payment_id': self.id,
            'journal_id': self.destination_journal_id.id})
        aml_obj.create(dst_liquidity_aml_dict)

        transfer_debit_aml_dict = self._get_shared_move_line_vals(credit, debit, 0, dst_move.id)
        transfer_debit_aml_dict.update({
            'name': _('Transfer to %s') % self.destination_journal_id.name,
            'payment_id': self.id,
            'account_id': cuenta_efectivo.id,
            'journal_id': self.destination_journal_id.id})
        if self.currency_id != self.company_id.currency_id:
            transfer_debit_aml_dict.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.amount,
            })
        transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        dst_move.post()
        return transfer_debit_aml

    @api.multi
    def itf_line_move_get(self, rec, currency):
        res = []
        journal = rec.journal_id
        itf_tax = self.env['account.gastos_bancarios'].search([('name', '=like', 'ITF%')], limit=1)
        cargos_account = self.env['account.account'].search([('code', '=like', '791%')], limit=1)
        # Creacion 1er asiento contable
        move_line_itf = {
            'type': 'src',
            'name': 'ITF',
            'price_unit': rec.amount * (itf_tax.amount / 100),
            'price': rec.amount * (itf_tax.amount / 100),
            'quantity': 1,
            'account_id': journal.itf_account_id.id,
        }
        res.append(move_line_itf)
        move_line_efectivo = {
            'type': 'src',
            'name': journal.name,
            'price_unit': -(rec.amount * (itf_tax.amount / 100)),
            'price': -(rec.amount * (itf_tax.amount / 100)),
            'quantity': 1,
            'account_id': journal.default_debit_account_id.id,
        }
        res.append(move_line_efectivo)
        # Creacion 2do asiento contable
        move_line_destino_itf = {
            'type': 'src',
            'name': itf_tax.name,
            'price_unit': rec.amount * (itf_tax.amount / 100),
            'price': rec.amount * (itf_tax.amount / 100),
            'quantity': 1,
            'account_id': itf_tax.destino_cuenta.id,
        }
        res.append(move_line_destino_itf)
        move_line_cargas_itf = {
            'type': 'src',
            'name': cargos_account.name,
            'price_unit': -(rec.amount * (itf_tax.amount / 100)),
            'price': -(rec.amount * (itf_tax.amount / 100)),
            'quantity': 1,
            'account_id': cargos_account.id,
        }
        res.append(move_line_cargas_itf)

        return res

    def _create_transfer(self, amount):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconciliable move line
        """
        cuenta_salida = self.journal_id.default_credit_account_id.id
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, dummy = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
            amount, self.currency_id, self.company_id.currency_id)
        amount_currency = self.destination_journal_id.currency_id and self.currency_id.with_context(
            date=self.payment_date).compute(amount, self.destination_journal_id.currency_id) or 0

        dst_move = self.env['account.move'].create(self._get_move_vals(self.destination_journal_id))

        dst_liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, dst_move.id)
        dst_liquidity_aml_dict.update({
            'name': _('Transfer from %s') % self.journal_id.name,
            'account_id': self.destination_journal_id.default_credit_account_id.id,
            'currency_id': self.destination_journal_id.currency_id.id,
            'payment_id': self.id,
            'journal_id': self.destination_journal_id.id})
        aml_obj.create(dst_liquidity_aml_dict)

        transfer_debit_aml_dict = self._get_shared_move_line_vals(credit, debit, 0, dst_move.id)
        transfer_debit_aml_dict.update({
            'name': _('Transfer to %s') % self.destination_journal_id.name,
            'payment_id': self.id,
            'account_id': cuenta_salida,
            'journal_id': self.destination_journal_id.id})
        if self.currency_id != self.company_id.currency_id:
            transfer_debit_aml_dict.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.amount,
            })
        transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        dst_move.post()

        # Inicio Segundo Asiento
        account_move = self.env['account.move']
        ctx = dict(self._context, lang=self.partner_id.lang)

        date_payment = fields.Date.context_today(self)
        company_currency = self.company_id.currency_id

        pml = self.itf_line_move()
        part = self.env['res.partner']._find_accounting_partner(self.partner_id)
        line = [(0, 0, self.env['account.invoice'].line_get_convert(l, part.id)) for l in pml]

        # 2do Asiento
        line1 = []
        line1.append(line[0])
        line1.append(line[1])
        journal = self.journal_id.with_context(ctx)
        date = date_payment
        move_vals_1 = {
            'line_ids': line1,
            'journal_id': journal.id,
            'date': date,
        }

        ctx['company_id'] = self.company_id.id
        ctx_nolang = ctx.copy()
        ctx_nolang.pop('lang', None)

        move1 = account_move.with_context(ctx_nolang).create(move_vals_1)
        move1.post()


        #return True

        #Fin Segundo Asiento
        return transfer_debit_aml

    @api.multi
    def itf_line_move(self):
        res = []
        journal = self.journal_id
        itf_tax = self.env['account.tax'].search([('name', '=like', 'ITF%')], limit=1)
        cargos_account = self.env['account.account'].search([('code', '=like', '791%')], limit=1)

        # Creacion 2do asiento contable
        move_line_destino_itf = {
            'type': 'src',
            'name': itf_tax.account_id.name,
            'price_unit': self.amount ,
            'price': self.amount ,
            'quantity': 1,
            'account_id': itf_tax.account_id.id,
        }
        res.append(move_line_destino_itf)
        move_line_cargas_itf = {
            'type': 'src',
            'name': cargos_account.name,
            'price_unit': -(self.amount ),
            'price': -(self.amount),
            'quantity': 1,
            'account_id': cargos_account.id,
        }
        res.append(move_line_cargas_itf)

        return res

    def _create_transfer_itf(self, amount):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconciliable move line
        """
        cuenta_salida = self.tipo_impuesto.id_cuenta.id,
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, dummy = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
            amount, self.currency_id, self.company_id.currency_id)
        amount_currency = self.journal_id.currency_id and self.currency_id.with_context(
            date=self.payment_date).compute(amount, self.journal_id.currency_id) or 0

        dst_move = self.env['account.move'].create(self._get_move_vals(self.journal_id))

        dst_liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, dst_move.id)
        dst_liquidity_aml_dict.update({
            'name': _('Transferido desde %s') % self.journal_id.name,
            'account_id': cuenta_salida,
            'currency_id': self.currency_id.id,
            'payment_id': self.id,
            'journal_id': self.journal_id.id})
        aml_obj.create(dst_liquidity_aml_dict)

        transfer_debit_aml_dict = self._get_shared_move_line_vals(credit, debit, 0, dst_move.id)
        transfer_debit_aml_dict.update({
            'name': _('Transferido a %s') % self.tipo_impuesto.id_cuenta.name,
            'payment_id': self.id,
            'account_id': self.journal_id.default_credit_account_id.id,
            'journal_id': self.journal_id.id})
        if self.currency_id != self.company_id.currency_id:
            transfer_debit_aml_dict.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.amount,
            })
        transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        dst_move.post()

        #Validamos si tiene cuenta destino
        if self.tipo_impuesto.destino_cuenta.id != False:
            # Inicio Segundo Asiento
            account_move = self.env['account.move']
            ctx = dict(self._context, lang=self.partner_id.lang)

            date_payment = fields.Date.context_today(self)
            company_currency = self.company_id.currency_id

            pml = self.line_move_itf()
            part = self.env['res.partner']._find_accounting_partner(self.partner_id)
            line = [(0, 0, self.env['account.invoice'].line_get_convert(l, part.id)) for l in pml]

            # 2do Asiento
            line1 = []
            line1.append(line[0])
            line1.append(line[1])
            journal = self.journal_id.with_context(ctx)
            date = date_payment
            move_vals_1 = {
                'line_ids': line1,
                'journal_id': journal.id,
                'date': date,
            }

            ctx['company_id'] = self.company_id.id
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)

            move1 = account_move.with_context(ctx_nolang).create(move_vals_1)
            move1.post()

            # return True

        # Fin Segundo Asiento
        return transfer_debit_aml

    def line_move_itf(self):
        res = []
        journal = self.journal_id
        #itf_tax = self.env['account.tax'].search([('name', '=like', 'ITF%')], limit=1)
        cargos_account = self.env['account.account'].search([('code', '=like', '791%')], limit=1)

        # Creacion 2do asiento contable
        move_line_destino_itf = {
            'type': 'src',
            'name': self.tipo_impuesto.destino_cuenta.name,
            'price_unit': self.amount,
            'price': self.amount,
            'quantity': 1,
            'account_id': self.tipo_impuesto.destino_cuenta.id,
        }
        res.append(move_line_destino_itf)
        move_line_cargas_itf = {
            'type': 'src',
            'name': cargos_account.name,
            'price_unit': -(self.amount),
            'price': -(self.amount),
            'quantity': 1,
            'account_id': cargos_account.id,
        }
        res.append(move_line_cargas_itf)

        return res


    @api.model
    def default_get(self, fields):
        id_factura = 0
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            id_factura = invoice['id']
            rec['communication'] = invoice['reference'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['residual']
            rec['residual_detraccion'] = invoice['residual_detraccion_soles']
            if invoice['pagina_detraccion'] == True:
                if invoice['residual_detraccion_soles'] == 0:
                    rec['pago_detraccion'] = True
                    rec['contro_detraccion'] = 0

        config_det = self.env['account.config.settings'].search(
            [('company_id', '=', self.company_id.id)], order='id desc', limit=1)
        if config_det.detraccion == 'DO':  # Una sola cuenta detraccion
            rec['journal_id'] = config_det.diario_detraccion


        factura = self.env['account.invoice'].search([('id', '=',id_factura)], limit=1)
        bandera = 0
        if factura.invoice_line_ids:
            for line in factura.invoice_line_ids:
                if line.product_id.detraccion == True:
                    bandera = 1


        if bandera == 1:
            rec['aplica_detraccion'] = True


        return rec

    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        if len(self.invoice_ids) == 0:
            return
        if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
            self.payment_difference = self.amount - self._compute_total_invoices_amount()
        else:
            self.payment_difference = self._compute_total_invoices_amount() - self.amount

        if self.pago_detraccion==True:
            value = self.invoice_ids.monto_detraccion_soles
            self.control_detraccion = value - self.amount
            #if value!=0



    # @api.one
    # @api.depends('invoice_ids', 'amount_detraccion', 'payment_date', 'currency_id')
    # def _compute_diferencia_pago_detraccion(self):
    #     if len(self.invoice_ids) == 0:
    #         return
    #     if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
    #         #self.diferencia_pago_detraccion = self.amount_detraccion - self._compute_total_invoices_amount()
    #         self.diferencia_pago_detraccion = abs(self.invoice_ids.monto_detraccion - self.amount_detraccion)
    #     else:
    #         self.diferencia_pago_detraccion = abs(self.amount_detraccion - self.invoice_ids.monto_detraccion)

    # @api.onchange('tipo_residual')
    # def _onchange_tipo_residual(self):
    #     # id_factura = self.invoice_ids.id
    #     # factura = self.env['account.invoice'].search([('id', '=', id_factura)], limit=1)
    #     # #if self.amount != 0:
    #     # if self.tipo_residual == 'd':
    #     #     self.amount = factura.residual_detraccion
    #     # else:
    #     #     self.amount = factura.residual_factura
    #     if self.invoice_ids.id:
    #         if self.tipo_residual == 'd':
    #             # if self.invoce_ids.currency_id.id==3:
    #             #     value = self.invoice_ids.residual_detraccion
    #             #     fecha = self.invoce_ids.date_invoice
    #             #     if moneda.id==3:
    #             # else:
    #             self.amount = self.invoice_ids.residual_detraccion
    #         else:
    #             self.amount = self.invoice_ids.residual_factura

    # def _create_payment_entry(self, amount):
    #     """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
    #         Return the journal entry.
    #     """
    #     aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #     invoice_currency = False
    #     if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
    #         # if all the invoices selected share the same currency, record the paiement in that currency too
    #         invoice_currency = self.invoice_ids[0].currency_id
    #     debit, credit, amount_currency, currency_id = aml_obj.with_context(
    #         date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
    #                                                       invoice_currency)
    #
    #     move = self.env['account.move'].create(self._get_move_vals())
    #
    #     # Write line corresponding to invoice payment
    #     counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
    #     counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
    #     counterpart_aml_dict.update({'currency_id': currency_id})
    #     counterpart_aml = aml_obj.create(counterpart_aml_dict)
    #
    #     # Reconcile with the invoices
    #     if self.payment_difference_handling == 'reconcile' and self.payment_difference:
    #         writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #         amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
    #             self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
    #         # the writeoff debit and credit must be computed from the invoice residual in company currency
    #         # minus the payment amount in company currency, and not from the payment difference in the payment currency
    #         # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
    #         total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
    #         total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount,
    #                                                                                                      self.company_id.currency_id)
    #         if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
    #             amount_wo = total_payment_company_signed - total_residual_company_signed
    #         else:
    #             amount_wo = total_residual_company_signed - total_payment_company_signed
    #         # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
    #         # amount in the company currency
    #         if amount_wo > 0:
    #             debit_wo = amount_wo
    #             credit_wo = 0.0
    #             amount_currency_wo = abs(amount_currency_wo)
    #         else:
    #             debit_wo = 0.0
    #             credit_wo = -amount_wo
    #             amount_currency_wo = -abs(amount_currency_wo)
    #         writeoff_line['name'] = _('Counterpart')
    #         writeoff_line['account_id'] = self.writeoff_account_id.id
    #         writeoff_line['debit'] = debit_wo
    #         writeoff_line['credit'] = credit_wo
    #         writeoff_line['amount_currency'] = amount_currency_wo
    #         writeoff_line['currency_id'] = currency_id
    #         writeoff_line = aml_obj.create(writeoff_line)
    #         if counterpart_aml['debit']:
    #             counterpart_aml['debit'] += credit_wo - debit_wo
    #         if counterpart_aml['credit']:
    #             counterpart_aml['credit'] += debit_wo - credit_wo
    #         counterpart_aml['amount_currency'] -= amount_currency_wo
    #     self.invoice_ids.register_payment(counterpart_aml)
    #     if self.has_invoices == True:
    #         if self.aplica_detraccion == True:
    #             a=0
    #             #self.calculo_residual_factura_detraccion()
    #         else:
    #             b=0
    #             #self.calculo_residual_factura() # En caso de que el campo residual_factura este activo
    #
    #
    #     # Write counterpart lines
    #     if not self.currency_id != self.company_id.currency_id:
    #         amount_currency = 0
    #     liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
    #     liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
    #     aml_obj.create(liquidity_aml_dict)
    #
    #
    #
    #     move.post()
    #     return move

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        if self.trabajador == True:
            trab_id = self.lista_trabajador.address_home_id.id
            partner_id = self.env['res.partner'].search([('id','=',trab_id)],limit=1)
            return {
                'partner_id': partner_id.id,
                'invoice_id': invoice_id and invoice_id.id or False,
                'move_id': move_id,
                'debit': debit,
                'credit': credit,
                'amount_currency': amount_currency or False,
            }
        else:
            return {
                    'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                        'res.partner']._find_accounting_partner(self.partner_id).id or False,
                    'invoice_id': invoice_id and invoice_id.id or False,
                    'move_id': move_id,
                    'debit': debit,
                    'credit': credit,
                    'amount_currency': amount_currency or False,
                }

    # def calculo_residual_factura(self):
    #     self.invoice_ids.residual_factura = self.invoice_ids.residual_factura - self.amount
    #
    # def calculo_residual_factura_detraccion(self):
    #     if self.tipo_residual == 'f':
    #         self.invoice_ids.residual_factura = self.invoice_ids.residual_factura - self.amount
    #     else:
    #         self.invoice_ids.residual_detraccion = self.invoice_ids.residual_detraccion - self.amount

    def _get_liquidity_move_line_vals(self, amount):
        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name

        monto = self.invoice_ids.monto_detraccion_soles - amount

        # if self.invoice_ids.monto_detraccion_soles > 0:
        #     self.invoice_ids.residual_detraccion_soles = self.invoice_id.residual_detraccion_soles - amount
        #     if self.invoice_ids.type == 'in_invoice':
        #         account = self.invoice_ids.invoice_line_ids.product_id.cuenta_detraccion_compra.id
        #     else:
        #         account = self.invoice_ids.invoice_line_ids.product_id.cuenta_detraccion_venta.id
        #
        #     vals = {
        #         'name': name,
        #         'account_id': account,
        #         'payment_id': self.id,
        #         'journal_id': self.journal_id.id,
        #         'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        #     }
        # else:
        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound',
                                                'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
        # segundo asiento contable
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id,
                                                              self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    #Se reescribe este metodo para que al momento de seleccionar el tipo de pago, coloque en false la opcion trabajador
    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound':
                self.partner_type = 'customer'
                self.trabajador = False
            elif self.payment_type == 'outbound':
                self.partner_type = 'supplier'
                self.trabajador = False
            else:
                self.partner_type = False
                self.trabajador = False
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        res['domain']['journal_id'] = self.payment_type == 'inbound' and [
            ('at_least_one_inbound', '=', True)] or self.payment_type == 'outbound' and [
            ('at_least_one_outbound', '=', True)] or []
        res['domain']['journal_id'].append(('type', 'in', ('bank', 'cash')))
        return res



