# -*- coding: utf-8 -*-
from datetime import datetime, date

import bs4
import urllib2
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools import float_is_zero, float_compare

TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    #tipo_documento = fields.Many2one('einvoice.catalog.01', string=u'Tipo Documento',
    #                                 states={'draft': [('readonly', False)]})
    #tipo_nota_credito = fields.Many2one('einvoice.catalog.09', string=u'Tipo Nota de Crédito',
    #                                    states={'draft': [('readonly', False)]})
    #tipo_nota_debito = fields.Many2one('einvoice.catalog.10', string=u'Tipo Nota de Débito',
    #                                   states={'draft': [('readonly', False)]})
    tipo_comprobante_id = fields.Many2one('einvoice.catalog.01', string=u'Tipo Documento',
                                          states={'draft': [('readonly', False)]})
    numero_comprobante = fields.Char(u'Número de comprobante')
    # cbo_tipo_cambio = fields.Selection([('N', u'Ninguno'), ('C', u'Tipo Cambio Compra'), ('V', u'Tpo Cambio Venta')],
    #                                    string=u'Tipo de Cambio', default='N')
    # valor_tipo_cambio = fields.Float(string=u'Valor tipo Cambio', digits=(4, 3))

    invoice_id = fields.Many2one('account.invoice', string=u'Comprobante Relacionado')

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

    # CAMPOS PARA DETRACCIÓN
    pagina_detraccion = fields.Boolean(string='Constancia Depósito Detraccioón', default=False, store=True,
                                       states={'draft': [('readonly', False)]})
    numero_detraccion = fields.Char(string=u'Número', index=True,
                                    help='Ingrese el numero de referencia del comprobante de detraccion')
    fecha_emision_detraccion = fields.Date(string='Fecha de Emisión', index=True)
    # Monto de la detraccion a cobrar o a pagar
    monto_detraccion = fields.Monetary(string='Total Detraccion',
        store=True, readonly=True, compute='_compute_amount')
    monto_detraccion_soles = fields.Monetary(string='(Total Detraccion soles)',
                                       store=True, compute='_compute_amount')
    monto_factura = fields.Monetary(string='Total factura',
                                    store=True, readonly=True, compute='_compute_amount')
    residual_detraccion_soles = fields.Monetary(string="Cantidad a Pagar det.", readonly=True,store=True,
                                                compute='_compute_residual')
    cuenta_detraccion = fields.Char(string=u'Cuenta Det.')

    #Moneda por defecto en soles para la detraccion compras/ventas
    currency_id_soles = fields.Many2one('res.currency',string="Moneda soles", domain=[('id', '=', 163)], default=163)
    moneda = fields.Char(string='Moneda')

    state = fields.Selection(selection_add=[('anulada','Anulada')])


    # monto_factura_soles = fields.Monetary(string='Total factura soles',
    #                                 store=True, readonly=True, compute='_compute_monto_factura')
    #
    # residual_detraccion = fields.Monetary(string='Cantidad a pagar detraccion',readonly=True,
    #                                       compute='_compute_residual_factura'
    #    , store=True, help="Es el monto restante a pagar de la detraccion.")
    #
    # residual_factura = fields.Monetary(string='Cantidad a pagar factura',readonly=True, store=True,
    #                                    compute='_compute_residual_factura',
    #                                    help="Es el monto restante a pagar de la factura.")
    # residual_factura_soles = fields.Monetary(string='Factura soles',readonly=True,
    #                                          compute='_compute_residual_factura')
    # campos para operaciones
    codigo_total_descuentos = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '2005')])
    monto_descuentos = fields.Monetary(string=u'Monto Descuentos')
    codigo_total_operaciones_gravadas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1001')])
    monto_operaciones_gravadas = fields.Monetary(string=u'Monto operaciones gravadas')
    codigo_total_operaciones_inafectas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1002')])
    monto_operaciones_inafectas = fields.Monetary(string=u'Monto operaciones inafectas')
    codigo_total_operaciones_exoneradas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1003')])
    monto_operaciones_exoneradas = fields.Monetary(string=u'Monto operaciones Exoneradas')
    # codigo_percepcion = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '2001')])
    monto_base_imponible_percepcion = fields.Monetary(string=u'Monto base imponible percepcion')
    monto_percepcion = fields.Monetary(string=u'Monto percepcion')
    monto_total_inc_percepcion = fields.Monetary(string=u'Monto total percepcion')
    codigo_total_operaciones_gratuitas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1004')])
    monto_operaciones_gratuitas = fields.Monetary(string=u'Monto operaciones Gratuitas')

    @api.multi
    @api.onchange('tipo_comprobante_id','company_id')
    def onchange_tipo_comprobante_id(self):
        if self.tipo_comprobante_id.id == 3:
            diario = self.env['account.journal'].search([('code', '=', 'RXH'),('company_id','=',self.company_id.id)], limit=1)
            self.journal_id = {}
            self.journal_id = diario

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
                #line['price'] = self.currency_id.round(line['price'])
                line['price'] = line['price']
            if self.tipo_comprobante_id.code == '07':
                if self.type == 'out_invoice':
                    total -= line['price']
                    total_currency -= line['amount_currency'] or line['price']
                else:
                    total += line['price']
                    total_currency += line['amount_currency'] or line['price']
                    line['price'] = - line['price']

            if self.tipo_comprobante_id.code == '08':
                if self.type == 'out_invoice':
                    total += line['price']
                    total_currency += line['amount_currency'] or line['price']
                    line['price'] = - line['price']
                else:
                    total -= line['price']
                    total_currency -= line['amount_currency'] or line['price']

        return total, total_currency, invoice_move_lines


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

            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals_two(company_currency,
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


    # @api.multi
    # @api.depends('invoice_line_ids.price_unit', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
    #              'type','invoice_line_ids.quantity')
    # def _compute_monto_factura(self):
    #     val_detraccion = 0.0
    #     val_factura = 0.0
    #     impuesto=0.0
    #     total = 0.0
    #     base = 0.0
    #     #round_curr = self.currency_id.round
    #     for invoice in self:
    #         if invoice.anulada == False:
    #             if invoice.amount_total_company_signed >= invoice.invoice_line_ids.product_id.monto_minimo_detraccion:
    #                 for line in invoice.invoice_line_ids:
    #                     if line.product_id.porcentaje_detraccion > 0:
    #                         base = round(line.price_unit * line.quantity, 2)
    #                         for tax in line.invoice_line_tax_ids:
    #                             if len(tax.ids) > 0:
    #                                 if tax.price_include == True:
    #                                     impuesto = 0.0
    #                                 else:  # Siempre y cuando el impuesto no este incluido en el precio
    #                                     impuesto += base * (tax.amount / 100)
    #
    #                         total += (base + impuesto)
    #                         val_detraccion = total * (line.product_id.porcentaje_detraccion / 100)
    #                         val_factura = total - val_detraccion
    #
    #                     else:
    #                         if invoice.tipo_comprobante_id.id == 3:
    #                             val_factura = invoice.amount_total
    #                         else:
    #                             base += round(line.price_unit * line.quantity, 2)
    #                             for tax in line.invoice_line_tax_ids:
    #                                 if len(tax.ids) > 0:
    #                                     if tax.price_include == True:
    #                                         impuesto = 0.0
    #                                     else:  # Siempre y cuando el impuesto no este incluido en el precio
    #                                         impuesto += base * (tax.amount / 100)
    #
    #                             val_factura = (base + impuesto)
    #                             impuesto=0.0
    #             else:
    #                 for line in self.invoice_line_ids:
    #                     base += round(line.price_unit * line.quantity, 2)
    #                     for tax in line.invoice_line_tax_ids:
    #                         if len(tax.ids) > 0:
    #                             if tax.price_include == True:
    #                                 impuesto = 0.0
    #                             else:  # Siempre y cuando el impuesto no este incluido en el precio
    #                                 impuesto += base * (tax.amount / 100)
    #
    #                     val_factura = (base + impuesto)
    #                     impuesto = 0.0
    #
    #             invoice.monto_detraccion = val_detraccion
    #             invoice.monto_factura = val_factura
    #             if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
    #                 currency_id = self.currency_id.with_context(date=self.date_invoice)
    #                 val_detraccion = currency_id.compute(val_detraccion, self.company_id.currency_id)
    #                 val_factura = currency_id.compute(val_factura, self.company_id.currency_id)
    #             invoice.monto_detraccion_soles = val_detraccion
    #             invoice.monto_factura_soles = val_factura

    # @api.multi
    # @api.onchange('impuesto_renta')
    # def onchange_impuesto_renta(self):
    #     self.monto_impuesto_renta = sum(line.price_subtotal for line in self.invoice_line_ids) * (
    #         self.impuesto_renta.amount / 100)
    #
    # @api.multi
    # @api.onchange('amount_untaxed')
    # def onchange_price_subtotal(self):
    #     self.monto_impuesto_renta = sum(line.price_subtotal for line in self.invoice_line_ids) * (
    #         self.impuesto_renta.amount / 100)

    # @api.multi
    # @api.onchange('date_invoice')
    # def onchange_date_invoice(self):
    #     self.cbo_tipo_cambio = 'N'
    #     self.valor_tipo_cambio = 0

    # @api.multi
    # @api.onchange('cbo_tipo_cambio')
    # def onchange_cbo_tipo_cambio(self):
    #
    #     valor_compra = 0
    #     valor_venta = 0
    #     sw = 0
    #     # self.invoice_line_ids = {}
    #     value_tipo_cambio = self.cbo_tipo_cambio
    #     if value_tipo_cambio == 'V' or value_tipo_cambio == 'C':
    #         # self.invoice_line_ids = {}
    #         fecha = self.date_invoice
    #         if fecha != False:
    #             dia = fecha[8:10]
    #             mes = fecha[5:7]
    #             anho = fecha[0:4]
    #             fecha_sist = datetime.now().date()
    #
    #             if str(fecha) > str(fecha_sist):
    #                 self.valor_tipo_cambio = 0
    #                 self.cbo_tipo_cambio = 'N'
    #                 warning = {
    #                     'title': _('Alerta!'),
    #                     'message': _('No hay tipo de cambio para esta fecha!'),
    #                 }
    #                 return {'warning': warning}
    #             else:
    #                 fec = date(int(anho), int(mes), int(dia))
    #                 dia_semana = fec.weekday()
    #                 mes_num = fec.month
    #
    #                 if dia_semana == 6 or dia_semana == 0:  # Comparamos si el dia de semana es sabado o domingo
    #                     if int(dia) == 1 and int(mes) == 1:
    #                         anho = str(int(anho) - 1)
    #                         mes = '12'
    #                         web = urllib2.urlopen(
    #                             "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
    #                         soup = bs4.BeautifulSoup(web, 'lxml')
    #                         # soup.prettify()
    #                         tabla = soup.find_all('table')[1]
    #                         # fila = tabla.find_all('tr')
    #                         valor_compra = tabla.find_all('td')[-2].text.strip()
    #                         valor_venta = tabla.find_all('td')[-1].text.strip()
    #                     else:
    #                         if dia_semana == 0 and int(dia) == 2:
    #                             mes = int(mes) - 1
    #                             if mes < 10:
    #                                 mes = '0' + str(mes)
    #                             web = urllib2.urlopen(
    #                                 "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
    #                             soup = bs4.BeautifulSoup(web, 'lxml')
    #                             tabla = soup.find_all('table')[1]
    #                             valor_compra = tabla.find_all('td')[-2].text.strip()
    #                             valor_venta = tabla.find_all('td')[-1].text.strip()
    #                         else:
    #                             if int(dia) == 1:
    #                                 mes = int(mes) - 1
    #                                 if mes < 10:
    #                                     mes = '0' + str(mes)
    #                                 web = urllib2.urlopen(
    #                                     "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
    #                                 soup = bs4.BeautifulSoup(web, 'lxml')
    #                                 # print soup.prettify()
    #                                 tabla = soup.find_all('table')[1]
    #                                 # fila = tabla.find_all('tr')
    #                                 valor_compra = tabla.find_all('td')[-2].text.strip()
    #                                 valor_venta = tabla.find_all('td')[-1].text.strip()
    #                             else:
    #                                 if dia_semana == 6:
    #                                     dia = int(dia) - 1
    #                                 else:
    #                                     if dia_semana == 0:
    #                                         dia = int(dia) - 2
    #
    #                                 web = urllib2.urlopen(
    #                                     "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
    #                                 soup = bs4.BeautifulSoup(web, 'lxml')
    #                                 # print soup.prettify()
    #                                 tabla = soup.find_all('table')[1]
    #                                 # fila = tabla.find_all('tr')
    #                                 tabla_sin_cabecera = tabla.find_all('tr')[1:]
    #                                 for row in tabla_sin_cabecera:
    #                                     pos = 0
    #                                     col = row.find_all('td')
    #                                     # print col
    #                                     for columna in col:
    #                                         valor_celda = columna.text.strip()
    #                                         tamanio_valor = len(valor_celda)
    #                                         if tamanio_valor <= 2:
    #                                             if (int(valor_celda) == int(dia)):
    #                                                 valor_compra = col[pos + 1].text.strip()
    #                                                 valor_venta = col[pos + 2].text.strip()
    #                                         pos = pos + 1
    #                 else:
    #                     web = urllib2.urlopen(
    #                         "http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")
    #                     soup = bs4.BeautifulSoup(web, 'lxml')
    #                     # print soup.prettify()
    #                     tabla = soup.find_all('table')[1]
    #                     # fila = tabla.find_all('tr')
    #                     tabla_sin_cabecera = tabla.find_all('tr')[1:]
    #
    #                     for row in tabla_sin_cabecera:
    #                         pos = 0
    #                         col = row.find_all('td')
    #                         # print col
    #                         for columna in col:
    #                             valor_celda = columna.text.strip()
    #                             tamanio_valor = len(valor_celda)
    #                             if tamanio_valor <= 2:
    #                                 if (int(valor_celda) == int(dia)):
    #                                     valor_compra = col[pos + 1].text.strip()
    #                                     valor_venta = col[pos + 2].text.strip()
    #                             pos = pos + 1
    #
    #                 if valor_compra == 0 and valor_venta == 0:
    #                     warning = {
    #                         'title': _('Alerta!'),
    #                         'message': _('No hay tipo de cambio para esta fecha!'),
    #                     }
    #                     return {'warning': warning}
    #                 else:
    #                     if self.cbo_tipo_cambio == 'V':
    #                         value = round(float(valor_venta), 4)
    #                         self.valor_tipo_cambio = value
    #                     else:
    #                         if self.cbo_tipo_cambio == 'C':
    #                             value = round(float(valor_compra), 4)
    #                             self.valor_tipo_cambio = value
    #                     return self.invoice_id.valor_tipo_cambio
    #         else:
    #             self.cbo_tipo_cambio = 'N'
    #             warning = {
    #                 'title': _('Alerta!'),
    #                 'message': _('Debe seleccionar la fecha de Recibo!'),
    #             }
    #             return {'warning': warning}
    #     else:
    #         self.valor_tipo_cambio = 0

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        total_impuesto = 0
        for line in self.invoice_line_ids:
            # price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
            #                                               self.partner_id)['taxes']
            # igv_compras = self.env['account.tax'].search([('id', '=', '2')], limit=1)
            # if len(taxes) == 2:
            #     taxes[0]['amount'] = (taxes[0]['base'] + (taxes[1]['base'] * (igv_compras.amount / 100))) * (
            #     self.invoice_line_ids.product_id.tipo_percepcion.amount / 100)
            #     taxes[1]['amount'] = taxes[1]['base'] * (igv_compras.amount / 100)
            #     monto_percepcion = taxes[0]['amount']
            #
            # for tax in taxes:
            #     val = self._prepare_tax_line_vals(line, tax)
            #     key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
            #
            #     if key not in tax_grouped:
            #         tax_grouped[key] = val
            #     else:
            #         tax_grouped[key]['amount'] += round(val['amount'], 2)
            #         tax_grouped[key]['base'] += round(val['base'], 2)
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']

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
                        if self.amount_total_company_signed > monto_detraccion:
                            self.pagina_detraccion = True
                            self.cuenta_bancaria_detraccion()
                        else:
                            self.pagina_detraccion = False

        return tax_grouped


    def cuenta_bancaria_detraccion(self):
        if self.company_id:
            config_det = self.env['account.config.settings'].search(
                [('company_id', '=', self.company_id.id)], order='id desc', limit=1)
            if config_det.detraccion=='DO': #Una sola cuenta detraccion
                diario_detraccion = config_det.diario_detraccion
                self.cuenta_detraccion = diario_detraccion.bank_acc_number
            else:
                self.cuenta_detraccion = u'Múltiples cuentas'
    # @api.one
    # @api.depends('currency_id', 'invoice_line_ids.price_subtotal', 'move_id.line_ids.currency_id')
    # def _compute_residual_factura(self):
    #     z = 0.0
    #     deb=0.0
    #     cred=0.0
    #     if len(self.payment_move_line_ids.ids) > 0:
    #         for pago in self.payment_move_line_ids:
    #             if pago.pago_factura==True:
    #                 if self.type=='out_invoice':
    #                     z += pago.credit
    #                     if z > self.monto_detraccion:
    #                         valor = z - self.monto_detraccion
    #                         self.residual_factura = self.monto_factura - valor
    #                         self.residual_detraccion = 0.0
    #                     else:
    #                         z += pago.credit
    #                         self.residual_factura = self.monto_factura - z
    #
    #                 else:
    #                     z += pago.debit
    #                     if z != pago.amount_currency: #Si es diferente quiere decir que hay variacion en la moneda
    #                         self.residual_factura = self.monto_factura - pago.amount_currency #Dolares
    #                         self.residual_factura_soles = self.monto_factura_soles - z
    #                     else:
    #                         self.residual_factura = self.monto_factura - z
    #             else:
    #                 if self.type == 'out_invoice':
    #                     z += pago.credit
    #                     deb += pago.debit
    #                     self.residual_detraccion = self.monto_detraccion - z
    #                     self.residual_factura = self.monto_factura - deb
    #                 else:
    #                     z += pago.debit
    #                     cred += pago.credit
    #                     self.residual_detraccion = self.monto_detraccion - z
    #                     self.residual_factura = self.monto_factura - cred
    #     else:
    #         residual_factura = self.monto_factura
    #         residual_detracion = self.monto_detraccion
    #         self.residual_factura = residual_factura
    #         self.residual_detraccion = residual_detracion
    #         self.residual_factura_soles = self.monto_factura_soles
    #         self.residual_detraccion_soles = self.monto_detraccion_soles
    #         a=1


    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        #residual_detraccion=0.0
        #residual_factura=1
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

        self.control_pago_detraccion() #Es para tener un control de los pagos de la detraccion

        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding

        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    def control_pago_detraccion(self):
        if self.payment_ids:
            for payment in self.payment_ids:
                if payment.id != False:
                    if payment.pago_detraccion:
                        self.residual_detraccion_soles = 0
                    else:
                        self.residual_detraccion_soles = self.monto_detraccion_soles
                else:
                    pass
        else:
            self.residual_detraccion_soles = self.monto_detraccion_soles
        # if self.amount_total == abs(residual):
        #     self.residual_detraccion_soles = self.monto_detraccion_soles
        # else:
        #     self.residual_detraccion_soles = 0


    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        account_id = False
        payment_term_id = False
        fiscal_position = False
        bank_id = False
        warning = {}
        domain = {}
        company_id = self.company_id.id
        p = self.partner_id if not company_id else self.partner_id.with_context(force_company=company_id)
        type = self.type
        if p:
            rec_account = p.property_account_receivable_id
            pay_account = p.property_account_payable_id
            if not rec_account and not pay_account:
                action = self.env.ref('account.action_account_config')
                msg = _(
                    'Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

            if type in ('out_invoice', 'out_refund'):
                account_id = rec_account.id
                payment_term_id = p.property_payment_term_id.id
            else:
                if self.is_recibo == True: #En caso sea recibo
                    cuenta = self.env['account.account'].search([('code', '=', '424000')], limit=1)
                    account_id = cuenta.id
                else:
                    account_id = pay_account.id
                payment_term_id = p.property_supplier_payment_term_id.id

            delivery_partner_id = self.get_delivery_partner_id()
            fiscal_position = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id,
                                                                                      delivery_id=delivery_partner_id)

            # If partner has no warning, check its company
            if p.invoice_warn == 'no-message' and p.parent_id:
                p = p.parent_id
            if p.invoice_warn != 'no-message':
                # Block if partner only has warning but parent company is blocked
                if p.invoice_warn != 'block' and p.parent_id and p.parent_id.invoice_warn == 'block':
                    p = p.parent_id
                warning = {
                    'title': _("Warning for %s") % p.name,
                    'message': p.invoice_warn_msg
                }
                if p.invoice_warn == 'block':
                    self.partner_id = False

        self.account_id = account_id
        self.payment_term_id = payment_term_id
        self.date_due = False
        self.fiscal_position_id = fiscal_position

        if type in ('in_invoice', 'out_refund'):
            bank_ids = p.commercial_partner_id.bank_ids
            bank_id = bank_ids[0].id if bank_ids else False
            self.partner_bank_id = bank_id
            domain = {'partner_bank_id': [('id', 'in', bank_ids.ids)]}

        res = {}
        if warning:
            res['warning'] = warning
        if domain:
            res['domain'] = domain
        return res



class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    price_unit_dolars = fields.Float(string=u'Precio Unit $', required=True, default=0.0, digits=(6, 2))
    value_tipo_cambio = fields.Float(store=True, digits=(1, 2))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return

        part = self.invoice_id.partner_id
        #tipo_documento = self.invoice_id.tipo_documento
        #tipo_cambio = self.invoice_id.cbo_tipo_cambio
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

        # if tipo_cambio == False:
        #     warning = {
        #         'title': _('Alerta!'),
        #         'message': _('Debe seleccionar el tipo de cambio!'),
        #     }
        #     return {'warning': warning}

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

    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        if self.invoice_id.tipo_comprobante_id.id == 3:
            taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids
        else:
            if self.invoice_id.type in ('out_invoice', 'out_refund'):
                taxes = self.product_id.taxes_id or self.account_id.tax_ids
            else:
                taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids

        # Keep only taxes of the company
        company_id = self.company_id or self.env.user.company_id
        taxes = taxes.filtered(lambda r: r.company_id == company_id)

        self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes, self.product_id,
                                                                                          self.invoice_id.partner_id)

        fix_price = self.env['account.tax']._fix_tax_included_price
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            prec = self.env['decimal.precision'].precision_get('Product Price')
            if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price,
                                                    precision_digits=prec) == 0:
                self.price_unit = fix_price(self.product_id.standard_price, taxes, fp_taxes)
        else:
            self.price_unit = fix_price(self.product_id.lst_price, taxes, fp_taxes)