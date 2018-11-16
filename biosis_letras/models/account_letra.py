# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountLetra(models.Model):
    _name = 'account.letra'
    _rec_name = 'num_letra'
    _order = "id desc"

    @api.model
    def _default_currency(self):
        # tipo de moneda
        return self.env.user.company_id.currency_id

    @api.one
    @api.depends('facturas_lineas_ids.sub_total')
    def _compute_monto_total(self):
        self.monto_total = sum((line.sub_total) for line in self.facturas_lineas_ids)

    num_letra = fields.Char(u'Número', required=True, index=True, copy=False, default='Nuevo')
    numerocorrelativo = fields.Char(string=u'Nro correlativo de letra')
    partner_id = fields.Many2one('res.partner', string=u'Cliente', required=True)
    state = fields.Selection( [('draft', 'Borrador'), ('open', 'Abierto'), ('reconcile', 'Enviado a banco'), ('Cancel', 'Cancelado'),
         ('Renovated', 'Renovado'), ('Protested', 'Protestado'), ('charged', 'Cobrado')], default='draft')
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('account.letra'))

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=_default_currency, track_visibility='always')
    monto_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_monto_total')
    facturas_lineas_ids = fields.One2many('account.lines.letras', 'fact_id', copy=True)
    fechagiro = fields.Date(string=u'Fecha Giro')
    fechavencimiento = fields.Date(string=u'Fecha vencimiento')
    # campos de otra informacion
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Situación fiscal', oldname='fiscal_position',
                                         readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Diario', required=True, domain="[('type', '=','sale')]")
    account_id = fields.Many2one('account.account', string='Cuenta', required=True)
    #domain = "[('code', '=like','121%')]"
    move_id = fields.Many2one('account.move', string='Registro diario', readonly=True, index=True, ondelete='restrict', copy=False)
    move_name = fields.Char(string='Journal Entry Name', readonly=False,
                            default=False, copy=False,
                            help="Technical field holding the number given to the invoice, automatically set when the invoice is "
                                 "validated then stored to set the same number again if the invoice is cancelled, set to draft and "
                                 "re-validated.")
    type = fields.Char()
    # campos de pago

    #
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        partner_id = self.partner_id
        if partner_id:
            invoices = self.env['account.invoice'].search(
                [('partner_id', '=', partner_id.id), ('state', '=', 'open')])

            if invoices:
                account = self.env['account.account'].search([('code', '=like', '1210%')], limit=1)
                self.account_id = account
                diario = self.env['account.journal'].search([('code', '=', 'LET')], limit=1)
                self.journal_id = diario
                #pass
            else:
                raise UserError(('Este Cliente no tiene comprobantes'))

    # mostrar por defecto estado open
    @api.multi
    def state_open(self):

        secuencia = self.env['ir.sequence'].next_by_code('sequence.letra') or '/'

        if secuencia != '/':
            self.num_letra = secuencia
        self.write({'state': 'open'})
        self.type = 'out_refund'
        self.create_move()


    def create_move(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Por favor defina una secuencia en el diario de esta letra.'))
            if not inv.facturas_lineas_ids:
                raise UserError(_('Por favor relacione alguna factura para validar esta operación.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.fechagiro:
                inv.with_context(ctx).write({'fechagiro': fields.Date.context_today(self)})
            fecha_giro = inv.fechagiro
            company_currency = inv.company_id.currency_id
            iml = inv.letra_line_move_line()

            total, total_currency, iml = inv.with_context(ctx).compute_letras_totals(company_currency,iml)
            # añadir datos de payment
            # recuperar con el inv ingresado
            ###
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]

            journal = inv.journal_id.with_context(ctx)
            date = fecha_giro
            move_vals = {
                'ref': inv.num_letra,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': '',
            }
            ctx['company_id'] = inv.company_id.id
            ctx['dont_create_taxes'] = True
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)

            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        return True

    def letra_line_move_line(self):
        res = []
        account123_line = {
            'type': 'src',
            'name': self.journal_id.default_debit_account_id.name,
            'price_unit': self.monto_total,
            'price': self.monto_total,
            'quantity': 1,
            'account_id': self.journal_id.default_debit_account_id.id,
            'letra_id': self.id,
        }

        res.append(account123_line)

        account121_line = {
            'type': 'src',
            'name': self.account_id.name,
            'price_unit': self.monto_total * (-1),
            'price': self.monto_total * (-1),
            'quantity': 1,
            'account_id': self.account_id.id,
            'letra_id': self.id,
        }

        res.append(account121_line)

        return res

    @api.model
    def line_get_convert(self, line, part):
        return self.convert_prepared_anglosaxon_line(line, part)

    @api.model
    def convert_prepared_anglosaxon_line(self, line, partner):
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': partner,
            'name': line['name'],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids', []),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(
                line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'quantity': line.get('quantity', 1.00),
            'analytic_account_id': line.get('account_analytic_id', False),
            'analytic_tag_ids': line.get('analytic_tag_ids', False),
        }

    @api.multi
    def compute_letras_totals(self, company_currency, invoice_move_lines):
        total = 0
        total_currency = 0
        for line in invoice_move_lines:
            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(
                    date=self._get_currency_rate_date() or fields.Date.context_today(self))
                if not (line.get('currency_id') and line.get('amount_currency')):
                    line['currency_id'] = currency.id
                    line['amount_currency'] = currency.round(line['price'])
                    line['price'] = currency.compute(line['price'], company_currency)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = self.currency_id.round(line['price'])
            # if self.type in ('out_invoice', 'in_refund'):
            total += line['price']
            total_currency += line['amount_currency'] or line['price']
            line['price'] = - line['price']
            # else:
            #     total -= line['price']
            #     total_currency -= line['amount_currency'] or line['price']
        return total, total_currency, invoice_move_lines



class AccountLineLetra(models.Model):
    _name = 'account.lines.letras'
    _order = "fact_id,sequence,id"

    is_letra = fields.Boolean()
    fact_id = fields.Many2one('account.letra', ondelete='cascade', index=True)
    partner_id = fields.Many2one('res.partner', related='fact_id.partner_id', string='Partner')
    factura_relacionada = fields.Many2one('account.invoice', string='Factura relacionada')
    monto = fields.Float(string='Monto', required=True, digits=(5, 3))
    descripcion = fields.Char(string='Relacionado a')
    sub_total = fields.Monetary(string='Sub Total', store=True, readonly=True, compute='_compute_monto')
    sequence = fields.Integer(default=10, help="Secuencia para la linea")
    currency_id = fields.Many2one('res.currency', related='fact_id.currency_id', store=True, related_sudo=False)

    @api.one
    @api.depends('monto')
    def _compute_monto(self):
        self.sub_total = self.monto * 1

    @api.multi
    @api.onchange('factura_relacionada')
    def onchange_factura_relacionada(self):
        self.descripcion = self.factura_relacionada.partner_id.name
        self.monto = self.factura_relacionada.amount_total


    # Clase para para registrar banco
class LetrasBancos(models.Model):
    _name = 'letra.bank'
    _order = "id desc"
    _rec_name = 'bank_id'

    def _get_letra(self):
        letra_id = self._context['active_id']
        return letra_id

    id = fields.Char("Codigo")
    bank_id = fields.Many2one('account.journal', string=u'Banco', domain=[('type', '=', 'bank')])
    tipo_cuenta = fields.Char(string=u'Tipo de Cuenta', readonly=True)
    nrocuenta = fields.Char(string=u'Nro de cuenta', readonly=True)
    fechavencimiento = fields.Date(string=u'Fecha de Vencimiento', readonly=True, related='letra.fechavencimiento')
    letra = fields.Many2one('account.letra', u'Letra', default=_get_letra)

    # devuelve los nrodecuenta por id de bank    @api.onchange
    @api.multi
    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id:
            self.tipo_cuenta = "Ninguno"
            self.nrocuenta = self.bank_id.bank_acc_number

    @api.multi
    def post(self):
        self.letra.state = 'reconcile'


