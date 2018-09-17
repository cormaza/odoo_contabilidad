# -*- coding: utf-8 -*-
import base64
from zipfile import ZipFile

from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import os
import jinja2
import requests, json
import StringIO
# from zeep import Client
# from zeep.exceptions import Fault
# from zeep.wsse.username import UsernameToken
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)

path_xml = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'jinja2'))
loader = jinja2.FileSystemLoader(path_xml)
env = jinja2.Environment(loader=loader, autoescape=True)

TIPO_OPERACION = (
    ('1', u'VENTA INTERNA'),
    ('2', u'EXPORTACIÓN'),
    ('4', u'ANTICIPO O DEDUCCIÓN DE ANTICIPO EN VENTA INTERNA'),
)

MONEDA_SINGULAR = 'DOLAR'
MONEDA_PLURAL = 'DOLARES'

CENTIMOS_SINGULAR = 'CENTIMO'
CENTIMOS_PLURAL = 'CENTIMOS'

MAX_NUMERO = 999999999999

UNIDADES = (
    'cero',
    'uno',
    'dos',
    'tres',
    'cuatro',
    'cinco',
    'seis',
    'siete',
    'ocho',
    'nueve'
)

DECENAS = (
    'diez',
    'once',
    'doce',
    'trece',
    'catorce',
    'quince',
    'dieciseis',
    'diecisiete',
    'dieciocho',
    'diecinueve'
)

DIEZ_DIEZ = (
    'cero',
    'diez',
    'veinte',
    'treinta',
    'cuarenta',
    'cincuenta',
    'sesenta',
    'setenta',
    'ochenta',
    'noventa'
)

CIENTOS = (
    '_',
    'ciento',
    'doscientos',
    'trescientos',
    'cuatroscientos',
    'quinientos',
    'seiscientos',
    'setecientos',
    'ochocientos',
    'novecientos'
)


def numero_a_letras(numero):
    numero_entero = int(numero)
    if numero_entero > MAX_NUMERO:
        raise OverflowError('Número demasiado alto')
    if numero_entero < 0:
        return 'menos %s' % numero_a_letras(abs(numero))
    letras_decimal = ''
    parte_decimal = int(round((abs(numero) - abs(numero_entero)) * 100))
    if parte_decimal > 9:
        letras_decimal = 'punto %s' % numero_a_letras(parte_decimal)
    elif parte_decimal > 0:
        letras_decimal = 'punto cero %s' % numero_a_letras(parte_decimal)
    if (numero_entero <= 99):
        resultado = leer_decenas(numero_entero)
    elif (numero_entero <= 999):
        resultado = leer_centenas(numero_entero)
    elif (numero_entero <= 999999):
        resultado = leer_miles(numero_entero)
    elif (numero_entero <= 999999999):
        resultado = leer_millones(numero_entero)
    else:
        resultado = leer_millardos(numero_entero)
    resultado = resultado.replace('uno mil', 'un mil')
    resultado = resultado.strip()
    resultado = resultado.replace(' _ ', ' ')
    resultado = resultado.replace('  ', ' ')
    if parte_decimal > 0:
        resultado = '%s %s' % (resultado, letras_decimal)
    return resultado


def numero_a_moneda(numero, codigo_moneda):
    if codigo_moneda == 'PEN':
        MONEDA_SINGULAR = 'NUEVO SOL'
        MONEDA_PLURAL = 'NUEVOS SOLES'
    else:
        MONEDA_SINGULAR = 'DOLAR AMERICANO'
        MONEDA_PLURAL = 'DOLARES AMERICANOS'
    numero_entero = int(numero)
    parte_decimal = int(round((abs(numero) - abs(numero_entero)) * 100))
    centimos = ''
    if parte_decimal == 1:
        centimos = CENTIMOS_SINGULAR
    else:
        centimos = CENTIMOS_PLURAL
    moneda = ''
    if numero_entero == 1:
        moneda = MONEDA_SINGULAR
    else:
        moneda = MONEDA_PLURAL
    letras = numero_a_letras(numero_entero)
    letras = letras.replace('uno', 'un')
    if parte_decimal == 0:
        decimal_str = '00'
    else:
        decimal_str = str(parte_decimal)
    letras_decimal = 'Y %s/100' % decimal_str
    letras = '%s %s %s' % (letras, letras_decimal, moneda)
    return letras.upper()


# def numero_a_moneda(numero, cent_singular, cent_plural, mon_singular, mon_plural):
#     numero_entero = int(numero)
#     parte_decimal = int(round((abs(numero) - abs(numero_entero)) * 100))
#     centimos = ''
#     if parte_decimal == 1:
#         centimos = cent_singular
#     else:
#         centimos = cent_plural
#     moneda = ''
#     if numero_entero == 1:
#         moneda = mon_singular
#     else:
#         moneda = mon_plural
#     letras = numero_a_letras(numero_entero)
#     letras = letras.replace('uno', 'un')
#     letras_decimal = 'con %s %s' % (numero_a_letras(parte_decimal).replace('uno', 'un'), centimos)
#     letras = '%s %s %s' % (letras, moneda, letras_decimal)
#     return letras


def leer_decenas(numero):
    if numero < 10:
        return UNIDADES[numero]
    decena, unidad = divmod(numero, 10)
    if numero <= 19:
        resultado = DECENAS[unidad]
    elif numero == 20:
        resultado = DIEZ_DIEZ[decena]
    elif numero <= 29:
        resultado = 'veinti%s' % UNIDADES[unidad]
    else:
        resultado = DIEZ_DIEZ[decena]
        if unidad > 0:
            resultado = '%s y %s' % (resultado, UNIDADES[unidad])
    return resultado


def leer_centenas(numero):
    centena, decena = divmod(numero, 100)
    if numero == 0:
        resultado = 'cien'
    else:
        resultado = CIENTOS[centena]
        if decena > 0:
            resultado = '%s %s' % (resultado, leer_decenas(decena))
    return resultado


def leer_miles(numero):
    millar, centena = divmod(numero, 1000)
    resultado = ''
    if (millar == 1):
        resultado = ''
    if (millar >= 2) and (millar <= 9):
        resultado = UNIDADES[millar]
    elif (millar >= 10) and (millar <= 99):
        resultado = leer_decenas(millar)
    elif (millar >= 100) and (millar <= 999):
        resultado = leer_centenas(millar)
    resultado = '%s mil' % resultado
    if centena > 0:
        resultado = '%s %s' % (resultado, leer_centenas(centena))
    return resultado


def leer_millones(numero):
    millon, millar = divmod(numero, 1000000)
    resultado = ''
    if (millon == 1):
        resultado = ' un millon '
    if (millon >= 2) and (millon <= 9):
        resultado = UNIDADES[millon]
    elif (millon >= 10) and (millon <= 99):
        resultado = leer_decenas(millon)
    elif (millon >= 100) and (millon <= 999):
        resultado = leer_centenas(millon)
    if millon > 1:
        resultado = '%s millones' % resultado
    if (millar > 0) and (millar <= 999):
        resultado = '%s %s' % (resultado, leer_centenas(millar))
    elif (millar >= 1000) and (millar <= 999999):
        resultado = '%s %s' % (resultado, leer_miles(millar))
    return resultado


def leer_millardos(numero):
    millardo, millon = divmod(numero, 1000000)
    return '%s millones %s' % (leer_miles(millardo), leer_millones(millon))


class EInvoice(models.Model):
    _inherit = 'account.invoice'

    serie_id = fields.Many2one('biosis.facturacion.einvoice.serie', string=u'Serie')
    codigo_cliente = fields.Char(u'Código de cliente')
    correlativo = fields.Char('Correlativo')

    tipo_ncredito_id = fields.Many2one('einvoice.catalog.09', string=u'Tipo Nota de Crédito',
                                       states={'draft': [('readonly', False)]})
    tipo_ndebito_id = fields.Many2one('einvoice.catalog.10', string=u'Tipo Nota de Débito',
                                      states={'draft': [('readonly', False)]})
    tipo_operacion = fields.Selection(TIPO_OPERACION, default='1')
    invoice_id = fields.Many2one('account.invoice', string='Comprobante relacionado')

    total_descuentos = fields.Monetary(string=u'Total descuentos', default=0.00)
    # total_operaciones_gravadas = fields.Monetary(string=u'Total operaciones gravadas', store=True,compute='_compute_amount')
    total_operaciones_inafectas = fields.Monetary(string=u'Total operaciones inafectas', store=True,
                                                  compute='_compute_amount')
    total_operaciones_exoneradas = fields.Monetary(string=u'Monto operaciones Exoneradas', store=True,
                                                   compute='_compute_amount')
    total_operaciones_gratuitas = fields.Monetary(string=u'Monto operaciones Gratuitas', store=True,
                                                  compute='_compute_amount')
    total_operaciones_exportacion = fields.Monetary(string=u'Total operaciones exportación', store=True,
                                                    compute='_compute_amount')
    codigo_percepcion = fields.Char(string=u'Código percepción')
    codigo_registro_percepcion = fields.Char(string=u'Código registro percepción')
    total_inc_percepcion = fields.Monetary(string=u'Total inc percepción')
    total_base_imponible_percepcion = fields.Monetary(string=u'Monto base imponible percepcion')
    total_percepcion = fields.Monetary(string=u'Monto percepción')
    total_isc = fields.Monetary(string='Monto ISC')
    # codigo_total_descuentos = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '2005')])
    # codigo_total_operaciones_gravadas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1001')])
    # codigo_total_operaciones_inafectas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1002')])
    # codigo_total_operaciones_exoneradas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1003')])
    # codigo_percepcion = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '2001')])
    # codigo_total_operaciones_gratuitas = fields.Many2one('einvoice.catalog.14', domain=[('code', '=', '1004')])


    codigo_2d = fields.Char(u'Código bidimensional')
    total_cadena = fields.Char(u'Monto en letras')
    total_peso_neto = fields.Char('Peso neto total')
    total_peso_bruto = fields.Char('Peso bruto total')

    facturador_id = fields.Integer('Id en el facturador')
    digest_value = fields.Char('Digest value')
    signature_info = fields.Char('Signature info')
    enviado = fields.Boolean('enviado a sunat', default=False)

    comprobante_xml = fields.Binary()
    comprobante_cdr = fields.Binary()

    consignatario_id = fields.Many2one('biosis.facturacion.consignatario', string='Consignatario')
    puerto_embarque = fields.Many2one('biosis.facturacion.puertoembarque', string=u'Puerto de Embarque')
    puerto_destino = fields.Many2one('biosis.facturacion.puertodestino', string=u'Puerto de Destino')
    forma_pago = fields.Many2one('biosis.facturacion.formapago', string=u'Forma de Pago')
    condicion_venta = fields.Many2one('biosis.facturacion.condicionventa', string=u'Condicion de Venta')
    medio_transporte = fields.Many2one('biosis.facturacion.mediotransporte', string=u'Medio de transporte')
    certificado = fields.Text(string=u'Certificado',
                              default=u"BANANO ORGANICO CERTIFICADO GLOBAL G.A.P  GGN 4052852491785 "
                                      "\n CU: 812842")
    envio_ids = fields.One2many('einvoice.envio', 'einvoice_id')
    first_sale = fields.Text(string=u'Texto First Sale',
                             default=u'"We hereby declare that the above details and statements are correct and that the invoiced goods where wholly '
                                     u'\n the growth product or manufactured in PERU. We also declared that they comply with the origin requirements '
                                     u'\n specified for those goods in the applicable special free trade agreement for goods exported to the United States."')
    contingencia = fields.Boolean(string='Considerar contingencia', default=False)
    serie_contingencia = fields.Char(string='Serie de contingencia')
    correlativo_contingencia = fields.Char(string='Correlativo de contingencia')
    anulada = fields.Boolean(string='Anulada')

    @api.multi
    def name_get(self):
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Vendor Bill'),
            'out_refund': _('Refund'),
            'in_refund': _('Vendor Refund'),
        }
        result = []
        for inv in self:
            if inv.anulada:
                result.append((inv.id, "%s %s" % ('(ANULADA)', inv.numero_comprobante)))
            else:
                result.append((inv.id, "%s %s" % (inv.numero_comprobante or TYPES[inv.type], inv.name or '')))
        return result

    @api.multi
    def obtener_xml(self):
        for inv in self:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content?id=%s&model=account.invoice&field=comprobante_xml&filename=%s-%s-%s.XML' % (
                    inv.id, inv.company_id.partner_id.vat, inv.tipo_comprobante_id.code, inv.numero_comprobante),
                'target': 'new',
            }

    @api.multi
    def anular(self):
        # obtenemos el tipo de nota de credito primero
        tipo_ncredito_id = self.env['einvoice.catalog.09'].search([('code', '=', '01')]).id

        # generamos la nota de crédito para este caso
        conteo = 0
        nota_id = None
        for invoice in self:
            nota_id = invoice.generar_nota_credito(tipo_ncredito_id).get('credit_note_id')
            conteo += 1

        if conteo == 1:
            # mostramos el formulario nada mas
            view_id = self.env.ref('biosis_facturacion.biosis_facturacion_einvoice_form').id
            return {
                'name': u'Nota de crédito',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'res_model': 'account.invoice',
                'res_id': nota_id,
                'view_id': view_id,

            }
        elif conteo > 1:
            # Debemos retornar un tree view mostrando todas las notas generadas
            pass

    @api.multi
    def generar_nota_credito(self, tipo_ncredito_id):
        credit_note = None
        conteo = 0
        for invoice in self:
            serie_ori, correlativo_ori = invoice.numero_comprobante.split('-')
            serie = '%sN%s' % (serie_ori[0:1], serie_ori[2:])
            serie_id = self.env['biosis.facturacion.einvoice.serie'].search([('alfanumerico', '=', serie),
                                                                             ('company_id','=',invoice.company_id.id)]).id
            tipo_comprobante_id = self.env['einvoice.catalog.01'].search([('code', '=', '07')]).id
            credit_note_vals = {
                'invoice_id': invoice.id,
                'date_invoice': datetime.now().strftime('%Y-%m-%d'),
                'account_id': invoice.account_id.id,
                'tipo_operacion': invoice.tipo_operacion,
                'serie_id': serie_id,
                'partner_id': invoice.partner_id.id,
                'tipo_comprobante_id': tipo_comprobante_id,
                'reconciled': True,
                'tipo_ncredito_id': tipo_ncredito_id,
                'currency_id': invoice.currency_id.id
            }

            credit_note = self.env['account.invoice'].create(credit_note_vals)

            if credit_note.tipo_ncredito_id.code in ('01', '02'):
                invoice.write({'anulada': True,'state':'anulada'})

            # Copiar lineas de factura.
            for line in invoice.invoice_line_ids:
                line2 = line.copy()
                line2.write({'invoice_id': credit_note.id})

            conteo += 1
        if conteo == 1:
            return {'credit_note_id': credit_note.id}

    @api.multi
    def contingencia_content(self):
        lineas = []
        for inv in self:
            # serie, correlativo = inv.numero_comprobante.split('-')
            linea = ('*MOTIVO*',  # sera reemplazado
                     '0%s' % inv.tipo_operacion,
                     datetime.strptime(inv.date_invoice, "%Y-%m-%d").strftime('%d/%m/%Y'),  # fecha de factura
                     inv.tipo_comprobante_id.code,  # Tipo de comprobante
                     inv.serie_contingencia,  # Serie del comprobante
                     inv.correlativo_contingencia,  # Correlativo del comprobante
                     '',
                     inv.partner_id.catalog_06_id.code,
                     inv.partner_id.vat == '-' and '0' or inv.partner_id.vat,
                     inv.partner_id.name.strip(),
                     inv.currency_id.name,  # 11.- moneda
                     '%0.2f' % inv.amount_untaxed,  # 12. Operaciones gravadas
                     '%0.2f' % inv.total_operaciones_exoneradas,  # 13Operaciones exoneradas
                     inv.tipo_operacion == '2' and '0.00' or '%0.2f' % inv.total_operaciones_inafectas,
                     # 14 Operaciones inafectas
                     # inv.tipo_operacion == '2' and '%0.2f' % inv.total_operaciones_inafectas or '0.00',
                     '%0.2f' % inv.total_operaciones_exportacion,
                     # 15 Operaciones exportacion
                     '0.00',  # 16 ISC
                     '%0.2f' % inv.amount_tax,  # 17. TOTAL IGV
                     '0.00',  # 18. TOTAL OTROS TRIBUTOS
                     '%0.2f' % inv.amount_total,  # 19. IMPORTE TOTAL
                     '',
                     '',
                     '',
                     '',
                     '0.00',
                     '0.00',
                     '0.00',)
            lineas.append('|'.join(linea) + '|')
        return '\n'.join(lineas)

    @api.multi
    def obtener_cdr(self):
        for inv in self:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content?id=%s&model=account.invoice&field=comprobante_cdr&filename=R-%s-%s-%s.ZIP' % (
                    inv.id, inv.company_id.partner_id.vat, inv.tipo_comprobante_id.code, inv.numero_comprobante),
                'target': 'new',
            }

    def calculo_monto_recibo(self, round_curr):
        base = sum(line.price_subtotal for line in self.invoice_line_ids)
        tax = sum(round_curr(line.amount) for line in self.tax_line_ids)
        value = base + tax
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            value = currency_id.compute(value, self.company_id.currency_id)

        monto_minimo = 0
        for linea in self.tax_line_ids:
            if linea.tax_id.account_id.id == 832:
                monto_minimo = linea.tax_id.monto_minimo_impuesto_renta

        if value > monto_minimo:
            self.amount_tax = tax
            self.amount_untaxed = base
            self.amount_total = base - tax
        else:
            self.tax_line_ids = {}
            self.amount_tax = 0.0
            self.amount_untaxed = base
            self.amount_total = base

        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_total
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign


    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type')
    def _compute_amount(self):

        op_inafectas_cod = ['30', ]
        op_exoneradas_cod = ['20', ]
        op_exportacion = ['40', ]
        op_gravadas_cod = ['10', ]
        op_no_gratuitas_cod = ['10', '20', '30', '40']
        round_curr = self.currency_id.round
        self.total_operaciones_inafectas = round_curr(sum(
            line.price_subtotal for line in self.invoice_line_ids if line.tipo_igv_id.code in op_inafectas_cod))
        self.total_operaciones_exoneradas = round_curr(sum(
            line.price_subtotal for line in self.invoice_line_ids if line.tipo_igv_id.code in op_exoneradas_cod))
        self.total_operaciones_gratuitas = round_curr(sum(
            line.price_subtotal for line in self.invoice_line_ids if line.tipo_igv_id.code not in op_no_gratuitas_cod))
        self.total_operaciones_exportacion = round_curr(sum(
            line.price_subtotal for line in self.invoice_line_ids if line.tipo_igv_id.code in op_exportacion))
        # tax = round_curr(sum(line.total_igv for line in self.invoice_line_ids))

        if self.tipo_comprobante_id.id == 3:  # Se aplica para recibo por honorario
            self.calculo_monto_recibo(round_curr)

        else:
            if self.type == 'in_invoice':
                self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
                self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids)
                self.amount_total = self.amount_untaxed + self.amount_tax


            else:
                self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids if
                                          line.tipo_igv_id.code in op_gravadas_cod)
                self.amount_tax = round_curr(sum(line.total_igv for line in self.invoice_line_ids))
                self.amount_total = self.amount_untaxed + self.amount_tax + self.total_operaciones_gratuitas + \
                                    self.total_operaciones_exoneradas + self.total_operaciones_inafectas + self.total_operaciones_exportacion

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

            val_detraccion = sum(
                self.amount_total * (line.product_id.porcentaje_detraccion / 100) for line in self.invoice_line_ids
                if self.amount_total_company_signed > line.product_id.monto_minimo_detraccion
                )
            if self.amount_tax > 0:
                self.monto_detraccion = round(val_detraccion,1)
            else:
                val_detraccion = 0.0

            self.monto_factura = self.amount_total - val_detraccion

            if self.currency_id:
                self.moneda = self.currency_id.name
            if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
                currency_id = self.currency_id.with_context(date=self.date_invoice)
                val_detraccion = currency_id.compute(val_detraccion, self.company_id.currency_id)
            self.monto_detraccion_soles = val_detraccion
            self.residual_detraccion_soles = val_detraccion
            a=1


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
                        vals[field] = invoice._fields[field].convert_to_write(invoice[field], invoice)
        if not vals.get('account_id', False):
            raise UserError(_(
                'Configuration error!\nCould not find any account to create the invoice, are you sure you have a chart of account installed?'))

        invoice = super(EInvoice, self.with_context(mail_create_nolog=True)).create(vals)

        if any(line.invoice_line_tax_ids for line in invoice.invoice_line_ids) and not invoice.tax_line_ids:
            invoice.compute_taxes()

        return invoice

    @api.multi
    def creacion_movimiento(self):
        account_move = self.env['account.move']
        for inv in self:
            if not inv.tipo_comprobante_id:
                # Para casos en los que se deba manejar el tipo de comprobante automaticamente (POS)
                nro_documento = inv.partner_id.vat

                if len(nro_documento) == 8:
                    tipocomprobante = '03'
                    serie = 'B001'
                elif len(nro_documento) == 11:
                    tipocomprobante = '01'
                    serie = 'F001'
                else:
                    tipocomprobante = '03'
                    serie = 'B001'

                serie_id = self.env['biosis.facturacion.einvoice.serie'].search([('alfanumerico', '=', serie)],
                                                                                limit=1).id
                tipo_comprobante_id = self.env['einvoice.catalog.01'].search([('code', '=', tipocomprobante)],
                                                                             limit=1).id

                inv.write({'tipo_comprobante_id': tipo_comprobante_id, 'serie_id': serie_id})

            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            if self.tipo_comprobante_id.code in ['07', '08']:
                total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals_two(company_currency, iml)
            else:
                total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)
            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = \
                    inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(
                        total,
                        inv.date_invoice)[
                        0]
                res_amount_currency = total_currency
                ctx['date'] = inv.date or inv.date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            # inv.consignatario_id.write({'name': ' '.join(name.strip().split('\n'))})
            for line in inv.invoice_line_ids:
                line.write({'name': line.name.strip()})

            if inv.numero_comprobante:
                numero_documento = inv.numero_comprobante
                correlativo = inv.numero_comprobante.split('-')[1]
                _logger.info("Numero de documento y correlativo: %s %s" % (numero_documento, correlativo))
            else:
                correlativo = inv.serie_id.correlativo_id.next_by_id()
                _logger.info("Serie del invoice: %s" % inv.serie_id.alfanumerico)
                _logger.info("Nuevo correlativo a asignar: %s" % correlativo)
                numero_documento = '%s-%s' % (inv.serie_id.alfanumerico, correlativo)
            codigo_2d = '%s|%s|%s|%s|%s|%s|%s|%s|' % (
                inv.tipo_comprobante_id.code, inv.serie_id.alfanumerico, correlativo, inv.amount_tax,
                inv.amount_total,
                inv.date_invoice, inv.partner_id.catalog_06_id.code, inv.partner_id.vat)
            total_cadena = numero_a_moneda(inv.amount_total, inv.currency_id.name).upper()
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
                'numero_comprobante': numero_documento,
                'codigo_2d': codigo_2d,
                'total_cadena': total_cadena
            }
            inv.with_context(ctx).write(vals)
            inv.generar_xml()
        return True

    @api.multi
    def action_move_create_recibo(self):
        """ Creates invoice related analytics and financial move lines """
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
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals_recibo(company_currency, iml)

            name = inv.name or '/'
            iml.append({
                'type': 'dest',
                'name': name,
                'price': total,
                'account_id': inv.account_id.id,
                'date_maturity': inv.date_due,
                'amount_currency': diff_currency and total_currency,
                'currency_id': diff_currency and inv.currency_id.id,
                'invoice_id': inv.id
            })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
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

    @api.multi
    def compute_invoice_totals_recibo(self, company_currency, invoice_move_lines):
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

                if line['type'] == 'tax':
                    line['currency_id'] = currency.id
                    line['amount_currency'] = -1 * (currency.round(line['amount_currency']))
                    line['price'] = -1 * (currency.round(line['price']))
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = self.currency_id.round(line['price'])

                if line['type'] == 'tax':
                    valor = line['price']
                    line['price'] = -1 * valor

            total -= line['price']
            total_currency -= line['amount_currency'] or line['price']

        return total, total_currency, invoice_move_lines

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        invoice_line_gastos_ids = []
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                product_line = line.product_id
                if product_line:
                    if product_line.property_account_expense_id:
                        invoice_line_gastos_ids.append(line)

        if self.type == 'in_invoice':
            if len(invoice_line_gastos_ids) > 0:
                res = super(EInvoice, self).asiento_gastos(invoice_line_gastos_ids)
                self.action_move_create_recibo()
                return res
            else:
                return super(EInvoice, self).action_move_create()
        else:
            self.creacion_movimiento()

    @api.multi
    def regenerar_xml(self):
        for invoice in self:
            if not invoice.enviado:
                for line in invoice.invoice_line_ids:
                    total_igv = line.compute_total_igv()
                    line.write({'total_igv': total_igv})
                invoice.generar_xml()

    @api.multi
    def generar_xml(self):
        for invoice in self:
            firmaId = self.env['ir.config_parameter'].get_param('sunat.einvoice.firma_id')
            keystore_name = self.env['ir.config_parameter'].get_param('keystore.name')
            keystore_password = self.env['ir.config_parameter'].get_param('keystore.password')
            keystore_alias = self.env['ir.config_parameter'].get_param('keystore.alias')
            keystore_alias_password = self.env['ir.config_parameter'].get_param('keystore.alias.password')
            signer_url = self.env['ir.config_parameter'].get_param('einvoice.signer_url')
            invoice_xml = ''
            if invoice.tipo_comprobante_id.code == '01' or invoice.tipo_comprobante_id.code == '03':
                invoice_xml = env.get_template('invoice.xml').render({'invoice': invoice, 'firmaId': firmaId})
            elif invoice.tipo_comprobante_id.code == '07':
                invoice_xml = env.get_template('credit_note.xml').render({'invoice': invoice, 'firmaId': firmaId})

            data = {
                'comprobanteStr': invoice_xml,
                'firmaPosicion': 1,
                'firmaId': firmaId,
                'keystoreName': keystore_name,
                'keystorePassword': keystore_password,
                'keystoreAlias': keystore_alias,
                'keystoreAliasPassword': keystore_alias_password
            }
            resp = requests.post(url=signer_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
            firmado = json.loads(resp.text)

            invoice.write({
                'signature_info': firmado['signatureValue'],
                'digest_value': firmado['digestValue'],
                'comprobante_xml': firmado['comprobante']
            })

    def leer_estado_cdr(self, fichero):
        with fichero as contenido:
            bs = BeautifulSoup(contenido, ['lxml', 'xml'])
            cac_response = bs.find("cac:Response")
            codigo = cac_response.find('cbc:ResponseCode').get_text().strip()
            detalle = cac_response.find('cbc:Description').get_text().strip()

            return codigo, detalle, contenido

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'biosis_facturacion.report_einvoice_ticket')

    @api.multi
    def envio_automatico(self):
        maximo = timedelta(days=3)
        minimo = timedelta(days=7)

        fecha_actual = datetime.now().date()

        limite_superior = fecha_actual - minimo
        limite_inferior = fecha_actual - maximo

        invoices = self.env['account.invoice'].search(
            [('enviado', '=', False), ('date_invoice', '>=', limite_inferior), ('date_invoice', '<=', limite_superior),
             ('state', '=', 'open')])
        invoices.enviar_sunat()

    @api.multi
    def enviar_sunat(self):
        user = self.env['ir.config_parameter'].get_param('sunat.user')
        password = self.env['ir.config_parameter'].get_param('sunat.password')
        server_url = self.env['ir.config_parameter'].get_param('sunat.billservice_url')
        sender_url = self.env['ir.config_parameter'].get_param('einvoice.sender_url')
        envio_obj = self.env['einvoice.envio']
        # client = Client(server_url,
        #                 wsse=UsernameToken(username=user, password=password))
        for invoice in self:
            if not invoice.enviado:
                zip_buffer = StringIO.StringIO()
                comprobante_b64 = base64.decodestring(invoice.comprobante_xml)
                # xml_buffer.write(comprobante_b64)
                zip_archive = ZipFile(zip_buffer, mode="w")

                comprobante_nombre = '%s-%s-%s' % (
                    invoice.company_id.partner_id.vat, invoice.tipo_comprobante_id.code,
                    invoice.numero_comprobante)

                zip_archive.writestr('%s.XML' % comprobante_nombre, comprobante_b64)
                zip_archive.close()

                zip_value = zip_buffer.getvalue()

                # try:
                data = {
                    'comprobanteZIP': zip_value.encode("base64"),
                    'comprobanteNombre': comprobante_nombre,
                    'username': user,
                    'password': password
                }

                _logger.info("CDR %s" % data['comprobanteZIP'])

                resp = requests.post(url=sender_url, data=json.dumps(data),
                                     headers={'Content-Type': 'application/json'})

                resp = json.loads(resp.text)
                response = resp.get('cdrZIP', False)

                if response:
                    cdr_buffer = StringIO.StringIO()
                    cdr_buffer.write(base64.decodestring(response))

                    zip_cdr = ZipFile(cdr_buffer)
                    ficheros = zip_cdr.namelist()
                    _logger.info("FACTURA: %s FICHEROS EN CDR: %s" % (comprobante_nombre, ','.join(ficheros)))
                    xmls = [fichero for fichero in ficheros if fichero.endswith('.XML') or fichero.endswith('.xml')]

                    if len(xmls) == 0:
                        codigo = 'ERROR'
                        envio_obj.create({
                            'einvoice_id': invoice.id,
                            'codigo': codigo,
                            'detalle': 'NO DETALLADO',
                            'servidor': 'produccion',
                            'cdr': response
                        })
                    else:
                        cdr_file = zip_cdr.open(xmls[0])
                        codigo, detalle, contenido = self.leer_estado_cdr(cdr_file)

                        zip_cdr.close()
                        envio_obj.create({
                            'einvoice_id': invoice.id,
                            'codigo': codigo,
                            'detalle': detalle,
                            'servidor': 'produccion',
                            'cdr': response
                        })

                    if codigo == '0':
                        invoice.write({'enviado': True})
                        invoice.write({'comprobante_cdr': response})
                else:
                    envio_obj.create({
                        'einvoice_id': invoice.id,
                        'codigo': resp.get('codigo', 'NRESP'),
                        'detalle': resp.get('detalle', 'SIN RESPUESTA'),
                        'servidor': server_url
                    })


class EInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def _default_tipo_igv(self):
        tipo_igv_id = self.env['einvoice.catalog.07'].search([('code', '=', '10')], limit=1).id
        return tipo_igv_id

    numero_placa = fields.Char(string=u'Número de placa')
    tipo_igv_id = fields.Many2one('einvoice.catalog.07', string='Tipo IGV', default=_default_tipo_igv)
    total_igv = fields.Monetary(string='Total IGV', compute='_compute_price', store=True)

    @api.one
    @api.depends('price_unit_dolars', 'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)

        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price

        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        if self.tipo_igv_id.code == '10':
            if taxes != False:
                self.total_igv = taxes['total_included'] - taxes['total_excluded']
                # self.total_igv = self.price_subtotal * 0.18
        else:
            self.total_igv = 0.0

    @api.multi
    def _get_analytic_line(self):
        ref = self.invoice_id.number
        for inv in self.invoice_id:
            amount = self.price_subtotal_signed

        return {
            'name': self.name,
            'date': self.invoice_id.date_invoice,
            'account_id': self.account_analytic_id.id,
            'unit_amount': self.quantity,
            'amount': amount,
            'product_id': self.product_id.id,
            'product_uom_id': self.uom_id.id,
            'general_account_id': self.account_id.id,
            'ref': ref,
        }

    @api.onchange('tipo_igv_id')
    def tipo_igv_seleccionado(self):
        if self.tipo_igv_id.code in ['10', '20', '30']:
            pass
        else:
            self.invoice_line_tax_ids = []

    @api.multi
    def compute_total_igv(self):
        for line in self:
            round_curr = line.currency_id.round

            if line.tipo_igv_id.code == '10':
                total_igv = line.total_igv = 0.18 * line.price_subtotal
            else:
                total_igv = line.total_igv = 0.00
            return round_curr(total_igv)


class ComprobanteEnvio(models.Model):
    _name = 'einvoice.envio'
    _order = 'timestamp desc'

    einvoice_id = fields.Many2one('account.invoice', string='Comprobante')
    tipo_comprobante_id = fields.Many2one('einvoice.catalog.01', string='Tipo de comprobante',
                                          related='einvoice_id.tipo_comprobante_id')
    timestamp = fields.Datetime(default=fields.Datetime.now(), string='Fecha y hora')
    codigo = fields.Char(string='Codigo resultado')
    detalle = fields.Text(string='Detalle')
    servidor = fields.Char(string='Servidor')
    cdr = fields.Binary()
