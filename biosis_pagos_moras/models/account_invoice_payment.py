# -*- coding: utf-8 -*-
from StringIO import StringIO
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from odoo import api, fields, models, _
import base64


class PaymentInvoice(models.TransientModel):
    _name = 'account.invoice.payment'
    _description = u"Pago Masivo Facturas "

    fichero = fields.Binary(u'Archivo CREP')

    @api.multi
    def process_payment(self):
        data = []
        fichero = base64.decodestring(self.fichero)
        io = StringIO(fichero)

        i = 0
        while i < 2:
            linea = io.readline()
            if linea == '':
                i = i + 1
            else:
                if linea.find('EFECTIVO') == -1:
                    pass
                else:
                    line = linea.split()
                    inquilino = line[1][8:]
                    if inquilino != '':
                        monto = line[2].replace('"', '')
                        inquilino = inquilino
                    else:
                        inquilino = line[2]
                        monto = line[3]

                    fecha = line[0]
                    valores = {'referencia': inquilino, 'monto': monto, 'fecha_pago': fecha}
                    data.append(valores)

        for datos in data:
            self.pago_masivo(datos)

    @api.multi
    def pago_masivo(self, data):
        if data:
            referencia = data['referencia']
            facturas = self.env['account.invoice'].search([('origin', 'ilike', referencia), ('state', '=','open')])
            if facturas:
                monto_total = 0.0
                for factura in facturas:
                    monto_total = monto_total + factura.amount_total

                monto = data['monto'].replace(',', '')

                amount = float(monto)
                payment_difference = float(monto) - monto_total
                if payment_difference > 0:
                    suscripcion = self.env['sale.subscription'].search([('code', 'ilike', referencia)])
                    monto_suscripcion = suscripcion.amount_mora
                    suscripcion.amount_mora = monto_suscripcion - payment_difference
                    self.generar_boleta(factura, suscripcion.amount_mora)

                date = datetime.now().date()

                fecha = datetime.strptime(data['fecha_pago'], '%d/%m/%Y')

                data ={
                 'payment_type': 'inbound',
                 'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                 'partner_type': 'customer',
                 'partner_id': factura.partner_id.id,
                 'amount': amount,
                 'payment_difference' : payment_difference,
                 'currency_id': self.env['res.currency'].search([('name', '=', 'PEN')]).id,
                 'payment_date': fecha,
                 'journal_id': self.env['account.journal'].search([('code', '=', 'BNK1')], limit=1).id,
                 'state': 'draft',
                 'name': u'Efecto de Pago por importación de TXT '
                 }

                payment = self.env['account.payment'].create(data)
                payment.invoice_ids = factura

                payment.post()

    @api.multi
    def generar_boleta(self, invoice, line_monto_mora):
        conteo = 0
        boleta_id = self.env['einvoice.catalog.01'].search([('code', '=', '01')]).id
        serie_id = self.env['biosis.facturacion.einvoice.serie'].search([('alfanumerico', '=', 'F002'),
                                                                         ('company_id', '=', invoice.company_id.id)]).id
        boleta_vals = {
            'date_invoice': datetime.now().strftime('%Y-%m-%d'),
            'account_id': invoice.account_id.id,
            'tipo_operacion': invoice.tipo_operacion,
            'partner_id': invoice.partner_id.id,
            'tipo_comprobante_id': boleta_id,
            'serie_id': serie_id,
            'state': 'draft',
            'currency_id': invoice.currency_id.id,
            'is_boleta_mora': True
        }
        fact = self.env['account.invoice'].create(boleta_vals)
        line2 = {}
        for line in invoice.invoice_line_ids:
            line2 = line.copy()
            line2.price_unit = line_monto_mora
            descripcion = line2.name
            line2.name = u'Interés moratorio ' + descripcion
            line2.invoice_line_tax_ids = {}
            line2.write({'invoice_id': fact.id})
        return fact






