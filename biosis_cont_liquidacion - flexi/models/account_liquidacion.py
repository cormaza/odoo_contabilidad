# -*- coding: utf-8 -*-
import datetime
import calendar
from odoo import api, fields, models, _

class AccountLiquidacion(models.Model):
    _name = 'account.liquidacion'
    _inherit = ['mail.thread']
    _description = u'Liquidación'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.one
    @api.depends('liquidacion_line_ids.amount_total', 'currency_id', 'company_id', 'date_invoice',
                 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_total = sum(line.amount_total for line in self.liquidacion_line_ids)
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_signed = self.amount_total * sign

    serie_id = fields.Many2one('biosis.facturacion.einvoice.serie', string=u'Serie')
    numero = fields.Char(u'Número de comprobante')
    correlativo = fields.Char('Correlativo')
    amount_total = fields.Monetary('Total')
    tipo_documento = fields.Many2one('einvoice.catalog.01', string=u'Tipo Documento',
                                     states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Cliente', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='always')
    date_invoice = fields.Date(string=u'Fecha Liquidación',
                               readonly=True, states={'draft': [('readonly', False)]}, index=True,
                               help="Keep empty to use the current date", copy=False)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=_default_currency, track_visibility='always')
    amount_total = fields.Monetary(string='Total',
                                   store=True, readonly=True, compute='_compute_amount')
    date_due = fields.Date(string='Fecha de vencimiento',
        readonly=True, states={'draft': [('readonly', False)]}, index=True)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('account.liquidacion'))
    check_dua = fields.Boolean(string='Usa DUA?', default=False)

    ref_dua = fields.Char(string='Ref.')
    linea_area_dua = fields.Char(string='Linea Aérea')
    awb_dua = fields.Char(string='AWB')
    dam_dua = fields.Char(string="DAM")
    cont_dua = fields.Char(string='CONT.')
    ref_cli_dua = fields.Char(string='Ref. Cliente')

    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Vendor Refund'),
    ], readonly=True, index=True, change_default=True,
        default=lambda self: self._context.get('type', 'out_invoice'),
        track_visibility='always')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('open', 'Abierto'),
        ('confirmed', 'Confirmado'),
        ('cancel', 'Cancelado'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' status is used when the invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    liquidacion_line_ids = fields.One2many('account.liquidacion.line', 'liquidacion_id', string='Pagos' )



