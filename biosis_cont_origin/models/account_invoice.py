# -*- coding: utf-8 -*-
from datetime import datetime, date

import bs4
import urllib2
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    tipo_documento = fields.Many2one('einvoice.catalog.01', string=u'Tipo Documento',
                                     states={'draft': [('readonly', False)]})
    tipo_nota_credito = fields.Many2one('einvoice.catalog.09', string=u'Tipo Nota de Crédito',
                                        states={'draft': [('readonly', False)]})
    tipo_nota_debito = fields.Many2one('einvoice.catalog.10', string=u'Tipo Nota de Débito',
                                       states={'draft': [('readonly', False)]})

    cbo_tipo_cambio = fields.Selection([('N', u'Ninguno'), ('C', u'Tipo Cambio Compra'), ('V', u'Tpo Cambio Venta')],
                                       string=u'Tipo de Cambio', default='N')
    valor_tipo_cambio = fields.Float(string=u'Valor tipo Cambio', store=True, digits=(4, 3))

    invoice_id = fields.Many2one('account.invoice', string=u'Comprobante Relacionado')
    # Campos calculados del Comprobante solo para mostrar
    partner_id_two = fields.Many2one('res.partner', string='Persona/Empresa',
                                     readonly=True, states={'draft': [('readonly', False)]})
    lineas_detalles = fields.One2many('account.invoice.line', 'invoice_id', string='Lineas de comprobante',
                                      oldname='invoice_line', readonly=True, states={'draft': [('readonly', False)]},
                                      copy=True)
    date_invoice_two = fields.Date(string='Fecha de Comprobante',
                                   readonly=True, states={'draft': [('readonly', False)]}, index=True,
                                   help="Keep empty to use the current date", copy=True)
    lineas_impuestos = fields.One2many('account.invoice.tax', 'invoice_id', string='Lineas impuestos',
                                       oldname='tax_line',
                                       readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    amount_untaxed_two = fields.Monetary(string='Base Imponible',
                                         store=True, readonly=True, track_visibility='always')
    amount_tax_two = fields.Monetary(string='Impuesto',
                                     store=True, readonly=True)
    amount_total_two = fields.Monetary(string='Total',
                                       store=True, readonly=True)
    # journal_id_two = fields.Many2one('account.journal', string='Diario de Referencia',readonly=True, states={'draft': [('readonly', False)]})
    payments_widget_two = fields.Text()
    residual_two = fields.Monetary(string='Amount Due', store=True, help="Remaining amount due.")
    reconciled_two = fields.Boolean(string='Paid/Reconciled', store=True, readonly=True)
    outstanding_credits_debits_widget_two = fields.Text()
    account_id_two = fields.Many2one('account.account', string='Cuenta', states={'draft': [('readonly', False)]},
                                     readonly=True, domain=[('deprecated', '=', False)])

    tipo_documento_two = fields.Many2one('einvoice.catalog.01', string=u'Tipo Documento Modificado')

    type_two = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Vendor Refund'),
    ], index=True)

    cuo_invoice = fields.Char(string=u'CUO del Documento', related='move_id.cuo')
    ple_generado = fields.Boolean(string=u'Ple Generado', default=False)
    # campo impuesto a la renta
    monto_impuesto_renta = fields.Monetary(string=u'Monto Imp. Rentaa',
                                           store=True)
    check_impuesto_renta = fields.Boolean(string=u'Aplica Imp. Renta', store=True)
    # check_impuesto_renta_two = fields.Boolean(string=u'Aplica Imp. Renta')
    # impuesto_renta = fields.Many2one('account.tax', store=True, string='Tipo de Impuesto', domain=[('id', '=', 6)])
    impuesto_renta = fields.Many2one('account.tax', store=True, string='Tipo de Impuesto')
    # Campo solo usado cuando se guarden notas de credito/debito
    guardado = fields.Boolean(string=u'Guardado', store=True, default=False)

    # Campos para agregar la constacia de la detraccion si es que el producto estuviese afecta a la misma
    pagina_detraccion = fields.Boolean(string='Constancia Depósito Detraccioón', default=False,
                                       states={'draft': [('readonly', False)]})
    numero_detraccion = fields.Char(string=u'Número', index=True,
                                    help='Ingrese el numero de referencia del comprobante de detraccion')
    fecha_emision_detraccion = fields.Date(string='Fecha de Emisión', index=True)
    # Monto de la detraccion a cobrar o a pagar
    monto_detraccion = fields.Monetary(string='Total Detraccion',
        store=True, readonly=True, compute='_compute_monto_factura')
    monto_factura = fields.Monetary(string='Total factura',
        store=True, readonly=True, compute='_compute_monto_factura')

    residual_detraccion = fields.Monetary(string='Cantidad a pagar detraccion',compute='_compute_residual'
       , store=True, help="Es el monto restante a pagar de la detraccion.")
    residual_factura = fields.Monetary(string='Cantidad a pagar factura',compute='_compute_residual'
                                       , store=True, help="Es el monto restante a pagar de la factura.")
    # campos para operaciones
    codigo_total_descuentos = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '2005')])
    monto_descuentos = fields.Monetary(string=u'Monto Descuentos')
    codigo_total_operaciones_gravadas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1001')])
    monto_operaciones_gravadas = fields.Monetary(string=u'Monto operaciones gravadas')
    codigo_total_operaciones_inafectas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1002')])
    monto_operaciones_inafectas = fields.Monetary(string=u'Monto operaciones inafectas')
    codigo_total_operaciones_exoneradas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1003')])
    monto_operaciones_exoneradas = fields.Monetary(string=u'Monto operaciones Exoneradas')
    codigo_percepcion = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '2001')])
    monto_base_imponible_percepcion = fields.Monetary(string=u'Monto base imponible percepcion')
    monto_percepcion = fields.Monetary(string=u'Monto percepcion')
    monto_total_inc_percepcion = fields.Monetary(string=u'Monto total percepcion')
    codigo_total_operaciones_gratuitas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1004')])
    monto_operaciones_gratuitas = fields.Monetary(string=u'Monto operaciones Gratuitas')

    # residual_detraccion = fields.Monetary(string=u'Cantidad residual detracción', currency_field='currency_id',
    #                                       states={'draft': [('readonly', False)]},compute='_compute_residual',
    #                                       help="Monto residual del pago de la detraccion")

    # Fin de campos

    @api.model
    def create(self, vals):
        onchanges = {
            '_onchange_partner_id': ['account_id', 'payment_term_id', 'fiscal_position_id', 'partner_bank_id'],
            '_onchange_journal_id': ['currency_id'],
        }
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(invoice[field])
        if not vals.get('account_id', False):
            raise UserError(_(
                'Configuration error!\nCould not find any account to create the invoice,'
                ' are you sure you have a chart of account installed?'))

        if 'tipo_documento' in vals:
            if vals['tipo_documento'] == 8 or vals['tipo_documento'] == 9:
                vals['guardado'] = True
        invoice = super(AccountInvoice, self.with_context(mail_create_nolog=True)).create(vals)

        if any(line.invoice_line_tax_ids for line in invoice.invoice_line_ids) and not invoice.tax_line_ids:
            invoice.compute_taxes()

        return invoice

    @api.multi
    # def seleccion_comprobante(self, invoice_id):
    #     if invoice_id:
    #         invoice = self.env['account.invoice'].search([('id', '=', invoice_id)], limit=1)
    #         if invoice:
    #             res = {'value': {}}
    #             res['value']['partner_id_two'] = invoice.partner_id
    #             res['value']['partner_id'] = invoice.partner_id
    #             res['value']['lineas_detalles'] = invoice.invoice_line_ids
    #             res['value']['date_invoice_two'] = invoice.date_invoice
    #             res['value']['lineas_impuestos'] = invoice.tax_line_ids
    #             res['value']['amount_untaxed_two'] = invoice.amount_untaxed
    #             res['value']['amount_tax_two'] = invoice.amount_tax
    #             res['value']['amount_total_two'] = invoice.amount_total
    #             res['value']['payments_widget_two'] = invoice.payments_widget
    #             res['value']['residual_two'] = invoice.residual
    #             res['value']['outstanding_credits_debits_widget_two'] = invoice.outstanding_credits_debits_widget
    #             res['value']['journal_id'] = invoice.journal_id
    #             res['value']['account_id'] = invoice.account_id
    #             res['value']['account_id_two'] = invoice.account_id
    #             res['value']['type_two'] = invoice.type
    #             res['value']['type'] = invoice.type
    #             res['value']['tipo_documento_two'] = invoice.tipo_documento
    #             return res
    #     return False

    @api.multi
    def compute_invoice_totals_two(self, company_currency, invoice_move_lines):
        total = 0
        total_currency = 0
        for line in invoice_move_lines:
            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(date=self.date_invoice or fields.Date.context_today(self))
                if not (line.get('currency_id') and line.get('amount_currency')):
                    line['currency_id'] = currency.id
                    line['amount_currency'] = currency.round(line['price'])
                    line['price'] = currency.compute(line['price'], company_currency)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = self.currency_id.round(line['price'])
            if self.tipo_documento.id == 8:
                if self.type_two == 'out_invoice':
                    total -= line['price']
                    total_currency -= line['amount_currency'] or line['price']
                else:
                    total += line['price']
                    total_currency += line['amount_currency'] or line['price']
                    line['price'] = - line['price']

            if self.tipo_documento.id == 9:
                if self.type_two == 'out_invoice':
                    total += line['price']
                    total_currency += line['amount_currency'] or line['price']
                    line['price'] = - line['price']
                else:
                    total -= line['price']
                    total_currency -= line['amount_currency'] or line['price']

        return total, total_currency, invoice_move_lines

    @api.multi
    def action_move_create(self):
        # Verificar si el producto contiene cuenta(s) de gastos
        invoice_line_gastos_ids = []
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                product_line = line.product_id
                if product_line:
                    if product_line.property_account_expense_id:
                        invoice_line_gastos_ids.append(line)
        #if self.invoice_line_ids:
            #for line in self.invoice_line_ids:


        # if (self.tipo_documento.id == 8 or self.tipo_documento.id == 9) or (
        #     self.invoice_line_ids.product_id.detraccion == True):
        if (self.tipo_documento.id == 8 or self.tipo_documento.id == 9):
            account_move = self.env['account.move']
            for inv in self:
                if not inv.journal_id.sequence_id:
                    raise UserError(_('Please define sequence on the journal related to this invoice.'))
                if not inv.invoice_line_ids:
                    raise UserError(_('Please create some invoice lines.'))
                if inv.move_id:
                    continue

                ctx = dict(self._context, lang=inv.partner_id.lang)

                if not inv.date_invoice:
                    inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
                date_invoice = inv.date_invoice
                company_currency = inv.company_id.currency_id

                # create move lines (one per invoice line + eventual taxes and analytic lines)
                iml = inv.invoice_line_move_line_get()
                iml += inv.tax_line_move_line_get()
                diff_currency = inv.currency_id != company_currency

                # Verifico si el tipo de documento es solo nota credito/debito
                if self.tipo_documento.id == 8 or self.tipo_documento.id == 9:
                    total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals_two(company_currency, iml)
                    name = inv.name or '/'
                    diccionario = {
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id_two.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    }
                    iml.append(diccionario)
                # else:
                #     if self.type == 'in_invoice':  # Para compras
                #         # Verifico si el producto de la factura esta sujeto a detraccion
                #         if self.invoice_line_ids.product_id.detraccion == True:
                #             total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency,
                #                                                                                       iml)
                #             name = inv.name or '/'
                #             diccionario2 = {
                #                 'type': 'dest',
                #                 'name': name,
                #                 'price': total,
                #                 'account_id': inv.account_id.id,
                #                 'date_maturity': inv.date_due,
                #                 'amount_currency': diff_currency and total_currency,
                #                 'currency_id': diff_currency and inv.currency_id.id,
                #                 'invoice_id': inv.id
                #             }
                #             monto_minimo_detraccion = self.invoice_line_ids.product_id.monto_minimo_detraccion
                #             porcentaje_detraccion = self.invoice_line_ids.product_id.porcentaje_detraccion
                #             cuenta_detraccion_compra = self.invoice_line_ids.product_id.cuenta_detraccion_compra
                #             if (total <= 0):
                #                 total_cuenta_por_pagar_detraccion = total * (porcentaje_detraccion / 100)
                #                 total_cuenta_por_pagar_normal = total - total_cuenta_por_pagar_detraccion
                #                 if monto_minimo_detraccion <= (-1 * total):
                #                     iml.append({
                #                         'type': 'dest',
                #                         'name': name,
                #                         'price': total_cuenta_por_pagar_normal,
                #                         'account_id': inv.account_id.id,
                #                         'date_maturity': inv.date_due,
                #                         'amount_currency': diff_currency and total_currency,
                #                         'currency_id': diff_currency and inv.currency_id.id,
                #                         'invoice_id': inv.id
                #                     })
                #
                #                     iml.append({
                #                         'type': 'dest',
                #                         'name': name,
                #                         'price': total_cuenta_por_pagar_detraccion,
                #                         'account_id': cuenta_detraccion_compra.id,
                #                         'date_maturity': inv.date_due,
                #                         'amount_currency': diff_currency and total_currency,
                #                         'currency_id': diff_currency and inv.currency_id.id,
                #                         'invoice_id': inv.id
                #                     })
                #
                #                 else:
                #                     iml.append(diccionario2)
                #             else:
                #                 iml.append(diccionario2)
                #
                #             if len(invoice_line_gastos_ids) > 0:
                #                 self.asiento_gastos(invoice_line_gastos_ids)
                #
                #         else:
                #             iml.append(diccionario2)
                #     else:
                #         if self.type == 'out_invoice':  # Para ventas
                #             # Verifico si el producto de la factura esta sujeto a detraccion
                #             # if self.invoice_line_ids.product_id.sale_ok == True and self.invoice_line_ids.product_id.cuenta_detraccion_venta != False:
                #             #     total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(
                #             #         company_currency, iml)
                #             #     name = inv.name or '/'
                #             #     diccionario2 = {
                #             #         'type': 'dest',
                #             #         'name': name,
                #             #         'price': total,
                #             #         'account_id': inv.account_id.id,
                #             #         'date_maturity': inv.date_due,
                #             #         'amount_currency': diff_currency and total_currency,
                #             #         'currency_id': diff_currency and inv.currency_id.id,
                #             #         'invoice_id': inv.id
                #             #     }
                #             #     monto_minimo_detraccion = self.invoice_line_ids.product_id.monto_minimo_detraccion
                #             #     porcentaje_detraccion = self.invoice_line_ids.product_id.porcentaje_detraccion
                #             #     cuenta_detraccion_venta = self.invoice_line_ids.product_id.cuenta_detraccion_venta
                #             #     if (total >= 0):
                #             #         total_cuenta_por_pagar_detraccion = total * (porcentaje_detraccion / 100)
                #             #         total_cuenta_por_pagar_normal = total - total_cuenta_por_pagar_detraccion
                #             #         if monto_minimo_detraccion <= (total):
                #             #             iml.append({
                #             #                 'type': 'dest',
                #             #                 'name': name,
                #             #                 'price': total_cuenta_por_pagar_normal,
                #             #                 'account_id': inv.account_id.id,
                #             #                 'date_maturity': inv.date_due,
                #             #                 'amount_currency': diff_currency and total_currency,
                #             #                 'currency_id': diff_currency and inv.currency_id.id,
                #             #                 'invoice_id': inv.id
                #             #             })
                #             #
                #             #             iml.append({
                #             #                 'type': 'dest',
                #             #                 'name': name,
                #             #                 'price': total_cuenta_por_pagar_detraccion,
                #             #                 'account_id': cuenta_detraccion_venta.id,
                #             #                 'date_maturity': inv.date_due,
                #             #                 'amount_currency': diff_currency and total_currency,
                #             #                 'currency_id': diff_currency and inv.currency_id.id,
                #             #                 'invoice_id': inv.id
                #             #             })
                #             #
                #             #         else:
                #             #             iml.append(diccionario2)
                #             #     else:
                #             #         iml.append(diccionario2)
                #             #
                #             #     if len(invoice_line_gastos_ids) > 0:
                #             #         self.asiento_gastos(invoice_line_gastos_ids)
                #             #
                #             # else:
                #             #     iml.append(diccionario2)
                #             res = super(AccountInvoice, self).action_move_create()
                #             return res

                part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
                line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
                line = inv.group_lines(iml, line)

                journal = inv.journal_id.with_context(ctx)
                line = inv.finalize_invoice_move_lines(line)
                date = inv.date or date_invoice
                move_vals = {
                    'ref': inv.reference,
                    'line_ids': line,
                    'journal_id': journal.id,
                    'date': date,
                    'narration': inv.comment,
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
                # make the invoice point to that move
                vals = {
                    'move_id': move.id,
                    'date': date,
                    'move_name': move.name,
                }
                inv.with_context(ctx).write(vals)
            return True
        else:
            if len(invoice_line_gastos_ids) > 0:
                res = super(AccountInvoice, self).action_move_create()
                self.asiento_gastos(invoice_line_gastos_ids)
                return res

            else:
                res = super(AccountInvoice, self).action_move_create()
                return res

    # Asiento de gastos : cuenta 9 contra la 79
    def asiento_gastos(self, invoice_line_gastos_ids):
        account_move = self.env['account.move']
        # considerar traer invoice a traves del id proporcionado por self
        # inv = self.env['account.invoice'].search([('id','=',self.id)],limit=1)
        for inv in self:
            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice
            company_currency = inv.company_id.currency_id
            iml = inv.invoice_line_move_line_get_gasto(invoice_line_gastos_ids)

            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency,
                                                                                      iml)
            # añadir datos de payment
            # recuperar con el inv ingresado
            ###
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]

            journal = inv.journal_id.with_context(ctx)
            date = inv.date or date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
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

    @api.multi
    def invoice_line_move_line_get_gasto(self, line_gastos):

        res = []
        # Relacion de cuentas dependientes
        cuentas_gastos = []

        for line in line_gastos:
            producto = line.product_id
            if producto.account_92_id:
                if producto.account_92_id not in cuentas_gastos:
                    cuentas_gastos.append(producto.account_92_id)
            if producto.account_94_id:
                if producto.account_94_id not in cuentas_gastos:
                    cuentas_gastos.append(producto.account_94_id)
            if producto.account_95_id:
                if producto.account_95_id not in cuentas_gastos:
                    cuentas_gastos.append(producto.account_95_id)
            if producto.account_97_id:
                if producto.account_97_id not in cuentas_gastos:
                    cuentas_gastos.append(producto.account_97_id)

        # Cuenta imputable de costos y gastos
        cuenta_79 = self.env['account.account'].search([('code', '=like', '791%')], limit=1)

        # Recorremos las cuentas y creamos las move_line relacionadas
        for cuenta in cuentas_gastos:
            price_unit = 0.0
            price = 0.0
            for line in line_gastos:
                producto = line.product_id
                if producto.account_92_id == cuenta:
                    price_unit += line.price_unit * (producto.porcentaje_92 / 100)
                    price += line.price_subtotal * (producto.porcentaje_92 / 100)
                if producto.account_94_id == cuenta:
                    price_unit += line.price_unit * (producto.porcentaje_94 / 100)
                    price += line.price_subtotal * (producto.porcentaje_94 / 100)
                if producto.account_95_id == cuenta:
                    price_unit += line.price_unit * (producto.porcentaje_95 / 100)
                    price += line.price_subtotal * (producto.porcentaje_95 / 100)
                if producto.account_97_id == cuenta:
                    price_unit += line.price_unit * (producto.porcentaje_97 / 100)
                    price += line.price_subtotal * (producto.porcentaje_97 / 100)

            move_line_dict = {
                'type': 'src',
                'name': cuenta.name,
                'price_unit': price_unit,
                'price': price,
                'quantity': 1,
                'account_id': cuenta.id,
                'invoice_id': self.id,
            }
            res.append(move_line_dict)

        # DEFINIMOS PRICE_UNIT Y PRICE PARA CUENTA 79
        price_unit_79 = 0.0
        price_79 = 0.0
        for move_line in res:
            price_unit_79 += move_line['price_unit']
            price_79 += move_line['price']

        # Creamos la move_line para la cuenta 79
        cuenta_79_line = {
            'type': 'src',
            'name': cuenta_79.name,
            'price_unit': price_unit_79 * (-1),
            'price': price_79 * (-1),
            'quantity': 1,
            'account_id': cuenta_79.id,
            'invoice_id': self.id,
        }
        # Añadimos la cuenta 79 a la lista de cuentas
        res.append(cuenta_79_line)
        return res

    @api.multi
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type')
    def _compute_amount(self):
        #super(AccountInvoice, self)._compute_amount()
        #self.amount_untaxed = round(self.amount_untaxed, 2)
        #self.amount_tax = round(self.amount_tax, 2)
        #self.amount_total = round((self.amount_tax + self.amount_untaxed), 2)
        round_curr = self.currency_id.round
        self.amount_untaxed = round(sum(line.price_subtotal for line in self.invoice_line_ids),2)
        self.amount_tax = round(sum(round_curr(line.amount) for line in self.tax_line_ids),2)
        self.amount_total = round(self.amount_untaxed + self.amount_tax,2)
        #lineas para monto_factura
       #self.monto_factura = sum(line.price_subtotal if ine.product_id.porcentaje_detraccion =)
        # for line in self.invoice_line_ids:
        #     if line.product_id.porcentaje_detraccion >0:
        #         self.monto_detraccion += round(line.price_unit * line.quantity, 2)
        #     else:
        #         self.monto_factura += round(line.price_unit * line.quantity,2)

        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

        #linea para campos monto_factura y residual_factura

        # Con operacion Gravadas y no gravadas

    @api.multi
    @api.depends('invoice_line_ids.price_unit', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type','invoice_line_ids.quantity')
    def _compute_monto_factura(self):
        val_detraccion = 0.0
        val_factura = 0.0
        #porcentaje = 0.0
        if self.amount_total >= 700:
            for line in self.invoice_line_ids:
                if line.product_id.porcentaje_detraccion > 0:
                    #porcentaje = line.product_id.porcentaje_detraccion / 100
                    val_detraccion += (line.price_unit * line.quantity) * (line.product_id.porcentaje_detraccion / 100)
                    val_factura += (line.price_unit * line.quantity) - val_detraccion
                else:
                    val_factura += round(line.price_unit * line.quantity, 2)
        else:
            for line in self.invoice_line_ids:
                val_factura += round(line.price_unit * line.quantity, 2)

        self.monto_detraccion = val_detraccion
        self.monto_factura = val_factura


    @api.multi
    @api.onchange('impuesto_renta')
    def onchange_impuesto_renta(self):
        self.monto_impuesto_renta = sum(line.price_subtotal for line in self.invoice_line_ids) * (
            self.impuesto_renta.amount / 100)

    @api.multi
    @api.onchange('amount_untaxed')
    def onchange_price_subtotal(self):
        self.monto_impuesto_renta = sum(line.price_subtotal for line in self.invoice_line_ids) * (
            self.impuesto_renta.amount / 100)

    @api.multi
    @api.onchange('date_invoice')
    def onchange_date_invoice(self):
        self.cbo_tipo_cambio = 'N'
        self.valor_tipo_cambio = 0

    @api.multi
    @api.onchange('cbo_tipo_cambio')
    def onchange_cbo_tipo_cambio(self):
        # mes = "05"
        # anho = "2016"
        # web = urllib2.urlopen('http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias')
        valor_compra = 0
        valor_venta = 0
        sw = 0
        # self.invoice_line_ids = {}
        value_tipo_cambio = self.cbo_tipo_cambio
        if value_tipo_cambio == 'V' or value_tipo_cambio == 'C':
            # self.invoice_line_ids = {}
            fecha = self.date_invoice
            if fecha != False:
                dia = fecha[8:10]
                mes = fecha[5:7]
                anho = fecha[0:4]
                fecha_sist = datetime.now().date()
                # fecha_hoy = str(fecha_sist.year)+'-'+str(fecha_sist.month)+'-'+str(fecha_sist.day)
                # fecha_comprobante = str(int(anho))+'-'+str(int(mes))+'-'+str(int(dia))

                if str(fecha) > str(fecha_sist):
                    self.valor_tipo_cambio = 0
                    self.cbo_tipo_cambio = 'N'
                    warning = {
                        'title': _('Alerta!'),
                        'message': _('No hay tipo de cambio para esta fecha!'),
                    }
                    return {'warning': warning}
                else:
                    fec = date(int(anho), int(mes), int(dia))
                    dia_semana = fec.weekday()
                    mes_num = fec.month

                    if dia_semana == 6 or dia_semana == 0:  # Comparamos si el dia de semana es sabado o domingo
                        if int(dia) == 1 and int(mes) == 1:
                            anho = str(int(anho) - 1)
                            mes = '12'
                            web = urllib2.urlopen(
                                "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
                            soup = bs4.BeautifulSoup(web, 'lxml')
                            # soup.prettify()
                            tabla = soup.find_all('table')[1]
                            # fila = tabla.find_all('tr')
                            valor_compra = tabla.find_all('td')[-2].text.strip()
                            valor_venta = tabla.find_all('td')[-1].text.strip()
                        else:
                            if dia_semana == 0 and int(dia) == 2:
                                mes = int(mes) - 1
                                if mes < 10:
                                    mes = '0' + str(mes)
                                web = urllib2.urlopen(
                                    "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
                                soup = bs4.BeautifulSoup(web, 'lxml')
                                # print soup.prettify()
                                tabla = soup.find_all('table')[1]
                                # fila = tabla.find_all('tr')
                                valor_compra = tabla.find_all('td')[-2].text.strip()
                                valor_venta = tabla.find_all('td')[-1].text.strip()
                            else:
                                if int(dia) == 1:
                                    mes = int(mes) - 1
                                    if mes < 10:
                                        mes = '0' + str(mes)
                                    web = urllib2.urlopen(
                                        "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
                                    soup = bs4.BeautifulSoup(web, 'lxml')
                                    # print soup.prettify()
                                    tabla = soup.find_all('table')[1]
                                    # fila = tabla.find_all('tr')
                                    valor_compra = tabla.find_all('td')[-2].text.strip()
                                    valor_venta = tabla.find_all('td')[-1].text.strip()
                                else:
                                    if dia_semana == 6:
                                        dia = int(dia) - 1
                                    else:
                                        if dia_semana == 0:
                                            dia = int(dia) - 2

                                    web = urllib2.urlopen(
                                        "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
                                    soup = bs4.BeautifulSoup(web, 'lxml')
                                    # print soup.prettify()
                                    tabla = soup.find_all('table')[1]
                                    # fila = tabla.find_all('tr')
                                    tabla_sin_cabecera = tabla.find_all('tr')[1:]
                                    for row in tabla_sin_cabecera:
                                        pos = 0
                                        col = row.find_all('td')
                                        # print col
                                        for columna in col:
                                            valor_celda = columna.text.strip()
                                            tamanio_valor = len(valor_celda)
                                            if tamanio_valor <= 2:
                                                if (int(valor_celda) == int(dia)):
                                                    valor_compra = col[pos + 1].text.strip()
                                                    valor_venta = col[pos + 2].text.strip()
                                            pos = pos + 1
                                            # valor_compra = tabla.find_all('td')[-2].text.strip()
                                            # valor_venta = tabla.find_all('td')[-1].text.strip()
                                            # else:
                                            # sw = 1
                                            # pos = pos + 1

                                            # if sw == 1:
                                            #     warning = {
                                            #         'title': _('Alerta!'),
                                            #         'message': _('No existe tipo de cambio para esta fecha!'),
                                            #     }
                                            #     return {'warning': warning}
                    else:
                        web = urllib2.urlopen(
                            "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
                        soup = bs4.BeautifulSoup(web, 'lxml')
                        # print soup.prettify()
                        tabla = soup.find_all('table')[1]
                        # fila = tabla.find_all('tr')
                        tabla_sin_cabecera = tabla.find_all('tr')[1:]

                        for row in tabla_sin_cabecera:
                            pos = 0
                            col = row.find_all('td')
                            # print col
                            for columna in col:
                                valor_celda = columna.text.strip()
                                tamanio_valor = len(valor_celda)
                                if tamanio_valor <= 2:
                                    if (int(valor_celda) == int(dia)):
                                        valor_compra = col[pos + 1].text.strip()
                                        valor_venta = col[pos + 2].text.strip()
                                pos = pos + 1

                    if valor_compra == 0 and valor_venta == 0:
                        warning = {
                            'title': _('Alerta!'),
                            'message': _('No hay tipo de cambio para esta fecha!'),
                        }
                        return {'warning': warning}
                    else:
                        if self.cbo_tipo_cambio == 'V':
                            value = round(float(valor_venta), 4)
                            self.valor_tipo_cambio = value
                        else:
                            if self.cbo_tipo_cambio == 'C':
                                value = round(float(valor_compra), 4)
                                self.valor_tipo_cambio = value
                        return self.invoice_id.valor_tipo_cambio
            else:
                self.cbo_tipo_cambio = 'N'
                warning = {
                    'title': _('Alerta!'),
                    'message': _('Debe seleccionar la fecha de Recibo!'),
                }
                return {'warning': warning}
        else:
            self.valor_tipo_cambio = 0

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        total_impuesto = 0
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            igv_compras = self.env['account.tax'].search([('id', '=', '2')], limit=1)
            if len(taxes) == 2:
                taxes[0]['amount'] = (taxes[0]['base'] + (taxes[1]['base'] * (igv_compras.amount / 100))) * (
                self.invoice_line_ids.product_id.tipo_percepcion.amount / 100)
                taxes[1]['amount'] = taxes[1]['base'] * (igv_compras.amount / 100)
                monto_percepcion = taxes[0]['amount']

            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += round(val['amount'], 2)
                    tax_grouped[key]['base'] += round(val['base'], 2)

            for impuesto in taxes:
                total_impuesto += round(impuesto['amount'], 2)

            valor = line.product_id.detraccion
            if valor == True:
                cantidad = line.quantity
                precio = line.price_unit
                sub_total = cantidad * precio
                total = sub_total + total_impuesto
                monto_detraccion = line.product_id.monto_minimo_detraccion
                if monto_detraccion != False:
                    if monto_detraccion > 0:
                        if total > monto_detraccion:
                            self.pagina_detraccion = True
                        else:
                            self.pagina_detraccion = False

        # Lineas de codigo para que me muestre el tab dento de facturas de commpra relacionado a la constancia de detraccion
        # for linea in self.invoice_line_ids:
        #     valor = linea.product_id.detraccion
        #     if valor == True:
        #         cantidad = linea.quantity
        #         precio = linea.price_unit
        #         sub_total = cantidad * precio
        #
        #
        #
        # print id

        # cantidad = self.invoice_line_ids.quantity
        # precio = self.invoice_line_ids.price_unit
        # sub_total = cantidad * precio
        # total = sub_total + total_impuesto
        # monto_detraccion = self.invoice_line_ids.product_id.monto_minimo_detraccion
        # if monto_detraccion != False:
        #     if total >= monto_detraccion:
        #         self.pagina_detraccion = True

        return tax_grouped

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_detraccion=0.0
        residual_factura=0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id.internal_type in ('receivable', 'payable'):
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(
                        date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)
                    residual_factura += line.invoice_id.residual_factura
                    residual_detraccion += line.invoice_id.residual_detraccion


        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        #Lineas agregadas para residuales de factura y detraccion
        if self.state == 'draft':
            self.residual_factura = self.monto_factura
            self.residual_detraccion = self.monto_detraccion
        else:
            self.residual_factura = residual_factura
            self.residual_detraccion = residual_detraccion
        #self.residual_detraccion = self.monto_detraccion


        # if self.type == 'in_invoice':  # Compras
        #     if self.monto_detraccion != False:
        #         if residual == 0.0:
        #             self.residual_company_signed = 0.0
        #             self.residual = 0.0
        #             self.residual_signed = 0.0
        #         else:
        #             self.residual_company_signed = round((abs(residual_company_signed) * sign) - self.monto_detraccion,
        #                                                  2)
        #             self.residual = round(abs(residual) - self.monto_detraccion, 2)
        #             self.residual_signed = round(((abs(residual) * sign) - self.monto_detraccion), 2)
        #     else:
        #         self.residual = abs(residual)
        #         self.residual_company_signed = abs(residual_company_signed) * sign
        #         self.residual_signed = abs(residual) * sign
        # else:  # Ventas
        #     if self.monto_detraccion != 0:
        #         self.residual_company_signed = round((abs(residual_company_signed) * sign), 2)
        #         self.residual = round(abs(residual), 2)
        #         self.residual_signed = round(((abs(residual) * sign)), 2)
        #     else:
        #         self.residual = abs(residual)
        #         self.residual_company_signed = abs(residual_company_signed) * sign
        #         self.residual_signed = abs(residual) * sign
        #digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False



class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    operacion = fields.Selection([
        ('gravadas', 'Adq. Grav. Dest. a Operaciones Grav.'),
        ('gravadasNoGravadas', 'Adq. Grav. Dest. a Operaciones Grav. y No Grav.'),
        ('noGravadas', 'Adq. Grav. Dest. a Operaciones No Grav.'),
        ('adqNoGravadas', 'Adq. No Gravadas.')
    ], string=u'Operación', store=True)

    price_unit_dolars = fields.Float(string=u'Precio Unit $', required=True, default=0.0, digits=(6, 2))
    value_tipo_cambio = fields.Float(store=True, digits=(1, 2))


    @api.one
    @api.depends('value_tipo_cambio', 'price_unit_dolars', 'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'operacion',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
    def _compute_price(self):
        valor_factura = 0
        monto_detraccion_producto = 0
        #porcentaje = 0
        if self.product_id.monto_minimo_detraccion != 0.0:
            monto_detraccion_producto = self.product_id.monto_minimo_detraccion
            #porcentaje = self.product_id.porcentaje_detraccion
        else:
            if self.product_id.monto_minimo_detraccion == 0.0:
                monto_detraccion_producto = 0
                #porcentaje = 0
            else:
                monto_detraccion_producto = self.invoice_id.invoice_line_ids.purchase_id.order_line.product_id.monto_minimo_detraccion
                #porcentaje = self.invoice_id.invoice_line_ids.purchase_id.order_line.product_id.porcentaje_detraccion

        if monto_detraccion_producto == False:
            monto_detraccion_producto = 0
        #if porcentaje == False:
            #porcentaje = 0

        if self.invoice_id.id == False:
            if self.invoice_id.cbo_tipo_cambio == 'C' or self.invoice_id.cbo_tipo_cambio == 'V':
                valor_tipo_cambio = self.invoice_id.valor_tipo_cambio
                price_unit_dolars = self.invoice_id.invoice_line_ids.price_unit_dolars
                self.price_unit = valor_tipo_cambio * price_unit_dolars
                self.invoice_id.invoice_line_ids.value_tipo_cambio = 0
            else:
                if self.invoice_id.cbo_tipo_cambio == 'N' or self.invoice_id.cbo_tipo_cambio == False:
                    self.invoice_id.invoice_line_ids.value_tipo_cambio = 1

        else:
            # Cuando es 8 u 9 hace referencia a una nota de credito o debito
            if self.invoice_id.tipo_documento.id == 9 or self.invoice_id.tipo_documento.id == 8:
                if self.invoice_id.cbo_tipo_cambio == 'C' or self.invoice_id.cbo_tipo_cambio == 'V':
                    valor_tipo_cambio = self.invoice_id.valor_tipo_cambio
                    price_unit_dolars = self.invoice_id.invoice_line_ids.price_unit_dolars
                    self.price_unit = valor_tipo_cambio * price_unit_dolars
            else:
                valor_tipo_cambio = self.invoice_id.valor_tipo_cambio
                if valor_tipo_cambio > 0:
                    price_unit_dolars = self.invoice_id.invoice_line_ids.price_unit_dolars
                    self.price_unit = valor_tipo_cambio * price_unit_dolars
                    self.invoice_id.invoice_line_ids.value_tipo_cambio = 0

        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        igv_compras = self.env['account.tax'].search([('id', '=', '2')], limit=1)

        if self.invoice_id.type == 'in_invoice':  # leyendo comprobante de Compra
            if self.invoice_id.tipo_documento.id != 8:
                if self.invoice_id.tipo_documento.id != 9:
                    if self.operacion == 'adqNoGravadas':
                        self.invoice_line_tax_ids = None
                        self.discount = 0
                    else:
                        if self.product_id.percepcion == True:
                            precio = self.invoice_id.invoice_line_ids.purchase_id.order_line.price_unit
                            if precio == False:
                                precio = price
                                if precio == False:
                                    precio = self.price_unit

                            cantidad = self.quantity
                            igv = igv_compras.amount / 100
                            valor = (precio * cantidad) + (precio * cantidad * igv)
                            if self.product_id.monto_minimo_percepcion <= valor:
                                if len(self.invoice_line_tax_ids.ids) < 2:
                                    diccionario_compras = igv_compras
                                    diccionario_percepcion = self.product_id.tipo_percepcion
                                    self.invoice_line_tax_ids = diccionario_compras + diccionario_percepcion
                            else:
                                self.invoice_line_tax_ids = igv_compras

        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)

        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        # if porcentaje > 0:
        #     if taxes['total_included'] > monto_detraccion_producto:
        #         val_detraccion = taxes['total_included'] * (porcentaje / 100)
        #         val_factura = round(taxes['total_included'] - taxes['total_included'] * (porcentaje / 100), 2)
        #         if self.invoice_id.monto_detraccion != val_detraccion:
        #             self.invoice_id.monto_detraccion = 0.0
        #             self.invoice_id.monto_factura = 0.0
        #             self.invoice_id.monto_detraccion = round(val_detraccion, 2)
        #             self.invoice_id.monto_factura = round(val_factura, 2)
        #             self.invoice_id.residual_detraccion = round(val_detraccion, 2)
        #             self.invoice_id.residual_factura = round(val_factura, 2)
        #         self.invoice_id.residual = self.invoice_id.monto_detraccion + self.invoice_id.monto_factura
        # else:
        #     self.invoice_id.monto_factura = 0.0
        #     if taxes!= False:
        #         valor_factura += round(taxes['total_included'], 2)


        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed,
                                                                        self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return

        part = self.invoice_id.partner_id
        tipo_documento = self.invoice_id.tipo_documento
        tipo_cambio = self.invoice_id.cbo_tipo_cambio
        fpos = self.invoice_id.fiscal_position_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type

        if not part:
            warning = {
                'title': _('Alerta!'),
                'message': _('Primero debe seleccionar un asociado!'),
            }
            return {'warning': warning}

        if not tipo_documento:
            warning = {
                'title': _('Alerta!'),
                'message': _('Debe seleccionar el tipo de documento!'),
            }
            return {'warning': warning}

        if tipo_cambio == False:
            warning = {
                'title': _('Alerta!'),
                'message': _('Debe seleccionar el tipo de cambio!'),
            }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id

            self.name = product.partner_ref
            account = self.get_invoice_line_account(type, product, fpos, company)
            if account:
                self.account_id = account.id
            self._set_taxes()

            if type in ('in_invoice', 'in_refund'):
                if product.description_purchase:
                    self.name += '\n' + product.description_purchase
            else:
                if product.description_sale:
                    self.name += '\n' + product.description_sale

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if company and currency:
                if company.currency_id != currency:
                    self.price_unit = self.price_unit * currency.with_context(
                        dict(self._context or {}, date=self.invoice_id.date_invoice)).rate

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = self.env['product.uom']._compute_price(
                        product.uom_id.id, self.price_unit, self.uom_id.id)
        return {'domain': domain}
