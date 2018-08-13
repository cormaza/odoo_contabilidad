# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    cuo = fields.Char(String=u"CUO")
    ple_generado = fields.Boolean(string=u'Ple Generado', default=False)

    @api.multi
    def post(self):
        super(AccountMove, self).post()
        for move in self:
            secuencia = self.env['ir.sequence'].search([('code','=','biosis_cont.cuo')],limit=1)
            if not move.cuo:
                move.write({'cuo': secuencia.next_by_id()})
        return self




class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    numero_asiento = fields.Char(String=u'Número Asiento')
    ple_generado = fields.Boolean(string=u'Ple Generado', default=False)

    def auto_reconcile_lines(self):
        """ This function iterates recursively on the recordset given as parameter as long as it
            can find a debit and a credit to reconcile together. It returns the recordset of the
            account move lines that were not reconciled during the process.
        """
        if not self.ids:
            return self
        sm_debit_move, sm_credit_move = self._get_pair_to_reconcile()
        # there is no more pair to reconcile so return what move_line are left
        if not sm_credit_move or not sm_debit_move:
            return self

        field = self[0].account_id.currency_id and 'amount_residual_currency' or 'amount_residual'
        if not sm_debit_move.debit and not sm_debit_move.credit:
            # both debit and credit field are 0, consider the amount_residual_currency field because it's an exchange difference entry
            field = 'amount_residual_currency'
        if self[0].currency_id and all([x.currency_id == self[0].currency_id for x in self]):
            # all the lines have the same currency, so we consider the amount_residual_currency field
            field = 'amount_residual_currency'
        if self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded':
            field = 'amount_residual'
        elif self._context.get('skip_full_reconcile_check') == 'amount_currency_only':
            field = 'amount_residual_currency'
        # Reconcile the pair together
        amount_reconcile = min(sm_debit_move[field], -sm_credit_move[field])
        # Remove from recordset the one(s) that will be totally reconciled
        if amount_reconcile == sm_debit_move[field]:
            self -= sm_debit_move
        if amount_reconcile == -sm_credit_move[field]:
            self -= sm_credit_move

        # Check for the currency and amount_currency we can set
        currency = False
        amount_reconcile_currency = 0
        if sm_debit_move.currency_id == sm_credit_move.currency_id and sm_debit_move.currency_id.id:
            currency = sm_credit_move.currency_id.id
            amount_reconcile_currency = min(sm_debit_move.amount_residual_currency,
                                            -sm_credit_move.amount_residual_currency)

        amount_reconcile = min(sm_debit_move.amount_residual, -sm_credit_move.amount_residual)

        if self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded':
            amount_reconcile_currency = 0.0
            currency = self._context.get('manual_full_reconcile_currency')
        elif self._context.get('skip_full_reconcile_check') == 'amount_currency_only':
            currency = self._context.get('manual_full_reconcile_currency')

        if sm_credit_move.invoice_id.id > 0:
            if sm_debit_move.invoice_id.pagina_detraccion == False:
                if sm_credit_move.invoice_id.residual_factura > 0:
                    valor = sm_credit_move.invoice_id.residual_factura - sm_debit_move.amount_residual
                    if valor < 0:
                        sm_credit_move.invoice_id.residual_factura = 0.0
                    else:
                        sm_credit_move.invoice_id.residual_factura = valor
            else:
                valor = sm_credit_move.invoice_id.residual_detraccion + sm_credit_move.amount_residual
                if valor < 0:
                    sm_credit_move.invoice_id.residual_detraccion = 0.0
                    sm_credit_move.invoice_id.residual_factura = sm_credit_move.invoice_id.residual_factura + valor
                else:
                    sm_credit_move.invoice_id.residual_detraccion = valor
        else:
            if sm_debit_move.invoice_id.pagina_detraccion == False:
                if sm_debit_move.invoice_id.residual_factura > 0:
                    valor = sm_debit_move.invoice_id.residual_factura + sm_credit_move.amount_residual
                    if valor < 0:
                        sm_debit_move.invoice_id.residual_factura = 0.0
                    else:
                        sm_debit_move.invoice_id.residual_factura = valor
            else:
                valor = sm_debit_move.invoice_id.residual_detraccion + sm_credit_move.amount_residual
                if valor < 0:
                    sm_debit_move.invoice_id.residual_detraccion = 0.0
                    sm_debit_move.invoice_id.residual_factura = sm_debit_move.invoice_id.residual_factura + valor
                else:
                    sm_debit_move.invoice_id.residual_detraccion = valor




        # Esta línea permite hacer conciliacion de los campos agregados de facturas y detraccion con respecto a su residual
        # for linea in self:
        #     for line in linea.invoice_id:
        #         if line.pagina_detraccion == True:
        #             # #valor = factura.residual_factura - amount_reconcile
        #             valor = line.residual_detraccion - amount_reconcile
        #             if valor < 0:
        #                 line.residual_detraccion = 0.0
        #                 line.residual_factura = line.residual_factura + valor
        #             else:
        #                 line.residual_detraccion = valor
        #         else:
        #             if line.residual_factura != False:
        #                 valor = line.residual_factura - amount_reconcile
        #                 if valor > 0:
        #                     line.residual_factura = valor
        #                 else:
        #                     line.residual_factura = 0.0
        #                     line.residual_detraccion = line.residual_detraccion + valor
        #                     # print linea

        self.env['account.partial.reconcile'].create({
            'debit_move_id': sm_debit_move.id,
            'credit_move_id': sm_credit_move.id,
            'amount': amount_reconcile,
            'amount_currency': amount_reconcile_currency,
            'currency_id': currency,
        })

        return self.auto_reconcile_lines()
