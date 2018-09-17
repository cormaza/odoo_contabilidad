
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    cuo = fields.Char(String=u"CUO")
    cuo_month = fields.Char(String=u"CUO")
    ple_generado = fields.Boolean(string=u'Ple Generado', default=False)
    #Agreagado para manejar los tipos de asiento
    type_move = fields.Selection(selection=[('A','apertura'),('M','Movimiento'),('C','Cierre')],
                                 default='M',required=True)

    @api.multi
    def post(self):
        super(AccountMove, self).post()
        for move in self:
            secuencia = self.env['ir.sequence'].search([('code','=','biosis_cont.cuo')],limit=1)
            if not move.cuo:
                move.write({'cuo': secuencia.next_by_id()})

        for move in self:
            if move.journal_id.type == 'apertura':
                move.type_move = 'A'
            elif move.journal_id.type == 'cierre':
                move.type_move = 'C'

            i=1
            for line in move.line_ids.sorted(key=lambda line: line.id):
                line.write({'numero_asiento':move.type_move+str(i)})
                i+= 1
        return self





class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    numero_asiento = fields.Char(String=u'Número Asiento')
    #ple_generado = fields.Boolean(string=u'Ple Generado', default=False)
    pago_factura = fields.Boolean(default=False)
    pago_detraccion = fields.Boolean(default=False)


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

        self.env['account.partial.reconcile'].create({
            'debit_move_id': sm_debit_move.id,
            'credit_move_id': sm_credit_move.id,
            'amount': amount_reconcile,
            'amount_currency': amount_reconcile_currency,
            'currency_id': currency,
        })

        return self.auto_reconcile_lines()

    @api.model
    def create(self, vals):
        """ :context's key apply_taxes: set to True if you want vals['tax_ids'] to result in the creation of move lines for taxes and eventual
                adjustment of the line amount (in case of a tax included in price).

            :context's key `check_move_validity`: check data consistency after move line creation. Eg. set to false to disable verification that the move
                debit-credit == 0 while creating the move lines composing the move.

        """
        #lineas de codigo agregadas
        context = dict(self._context or {})
        amount = vals.get('debit', 0.0) - vals.get('credit', 0.0)
        if not vals.get('partner_id') and context.get('partner_id'):
            vals['partner_id'] = context.get('partner_id')
        move = self.env['account.move'].browse(vals['move_id'])
        account = self.env['account.account'].browse(vals['account_id'])
        if account.deprecated:
            raise UserError(_('You cannot use deprecated account.'))
        if 'journal_id' in vals and vals['journal_id']:
            context['journal_id'] = vals['journal_id']
        if 'date' in vals and vals['date']:
            context['date'] = vals['date']
        if 'journal_id' not in context:
            context['journal_id'] = move.journal_id.id
            context['date'] = move.date
        # we need to treat the case where a value is given in the context for period_id as a string

        #Creacion lienas TIPO DE CAMBIO
        # if 'invoice' in context:
        #     factura = context['invoice']
        #     if factura.cbo_tipo_cambio =='V' or factura.cbo_tipo_cambio =='C':
        #         if vals['debit'] == False:
        #             valor = vals['credit']
        #             vals['credit'] = round((valor * factura.valor_tipo_cambio),2)
        #         if vals['credit']==False:
        #             valor = vals['debit']
        #             vals['debit'] = round((valor * factura.valor_tipo_cambio),2)
        #Fin de creación de asiento con tipo de cambio incluido

        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            context['journal_id'] = context.get('search_default_journal_id')
        if 'date' not in context:
            context['date'] = fields.Date.context_today(self)
        journal = vals.get('journal_id') and self.env['account.journal'].browse(vals['journal_id']) or move.journal_id
        vals['date_maturity'] = vals.get('date_maturity') or vals.get('date') or move.date
        ok = not (journal.type_control_ids or journal.account_control_ids)

        if journal.type_control_ids:
            type = account.user_type_id
            for t in journal.type_control_ids:
                if type == t:
                    ok = True
                    break
        if journal.account_control_ids and not ok:
            for a in journal.account_control_ids:
                if a.id == vals['account_id']:
                    ok = True
                    break
        # Automatically convert in the account's secondary currency if there is one and
        # the provided values were not already multi-currency
        if account.currency_id and 'amount_currency' not in vals and account.currency_id.id != account.company_id.currency_id.id:
            vals['currency_id'] = account.currency_id.id
            if self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded':
                vals['amount_currency'] = 0.0
            else:
                ctx = {}
                if 'date' in vals:
                    ctx['date'] = vals['date']
                vals['amount_currency'] = account.company_id.currency_id.with_context(ctx).compute(amount,
                                                                                                   account.currency_id)

        if not ok:
            raise UserError(_(
                'You cannot use this general account in this journal, check the tab \'Entry Controls\' on the related journal.'))

        # Create tax lines
        tax_lines_vals = []
        if context.get('apply_taxes') and vals.get('tax_ids'):
            # Get ids from triplets : https://www.odoo.com/documentation/master/reference/orm.html#openerp.models.Model.write
            tax_ids = [tax['id'] for tax in self.resolve_2many_commands('tax_ids', vals['tax_ids']) if tax.get('id')]
            # Since create() receives ids instead of recordset, let's just use the old-api bridge
            taxes = self.env['account.tax'].browse(tax_ids)
            currency = self.env['res.currency'].browse(vals.get('currency_id'))
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            res = taxes.with_context(round=True).compute_all(amount,
                                                             currency, 1, vals.get('product_id'), partner)
            # Adjust line amount if any tax is price_include
            if abs(res['total_excluded']) < abs(amount):
                if vals['debit'] != 0.0: vals['debit'] = res['total_excluded']
                if vals['credit'] != 0.0: vals['credit'] = -res['total_excluded']
                if vals.get('amount_currency'):
                    vals['amount_currency'] = self.env['res.currency'].browse(vals['currency_id']).round(
                        vals['amount_currency'] * (res['total_excluded'] / amount))
            # Create tax lines
            for tax_vals in res['taxes']:
                if tax_vals['amount']:
                    tax = self.env['account.tax'].browse([tax_vals['id']])
                    account_id = (amount > 0 and tax_vals['account_id'] or tax_vals['refund_account_id'])
                    if not account_id: account_id = vals['account_id']
                    temp = {
                        'account_id': account_id,
                        'name': vals['name'] + ' ' + tax_vals['name'],
                        'tax_line_id': tax_vals['id'],
                        'move_id': vals['move_id'],
                        'partner_id': vals.get('partner_id'),
                        'statement_id': vals.get('statement_id'),
                        'debit': tax_vals['amount'] > 0 and tax_vals['amount'] or 0.0,
                        'credit': tax_vals['amount'] < 0 and -tax_vals['amount'] or 0.0,
                        'analytic_account_id': vals.get('analytic_account_id') if tax.analytic else False,
                    }
                    bank = self.env["account.bank.statement"].browse(vals.get('statement_id'))
                    if bank.currency_id != bank.company_id.currency_id:
                        ctx = {}
                        if 'date' in vals:
                            ctx['date'] = vals['date']
                        temp['currency_id'] = bank.currency_id.id
                        temp['amount_currency'] = bank.company_id.currency_id.with_context(ctx).compute(
                            tax_vals['amount'], bank.currency_id, round=True)
                    tax_lines_vals.append(temp)

        new_line = super(AccountMoveLine, self).create(vals)
        # lineas agregadas
        # if new_line.payment_id.tipo_residual=='f':
        #     new_line['pago_factura'] = True
        # else: #Esto en caso si pagara detracion y la diferencia paga la factura
        #     if new_line.payment_id.payment_difference < 0:
        #         new_line['pago_factura'] = True
        #     new_line['pago_detraccion'] = True

        for tax_line_vals in tax_lines_vals:
            # TODO: remove .with_context(context) once this context nonsense is solved
            self.with_context(context).create(tax_line_vals)

        if self._context.get('check_move_validity', True):
            move.with_context(context)._post_validate()

        return new_line
