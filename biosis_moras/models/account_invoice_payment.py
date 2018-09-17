# -*- coding: utf-8 -*-
from StringIO import StringIO
from datetime import datetime, date
from odoo import api, fields, models
import base64


class TxtImport(models.TransientModel):
    _name = 'account.invoice.payment'
    _description = u"Upload mora Txt "

    fichero = fields.Binary(u'Archivo CREP')

    @api.multi
    def process_payement(self):
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
                    valores = {'referencia': inquilino, 'monto': monto}
                    data.append(valores)

        for datos in data:
            self.pago_masivo(datos)


    @api.multi
    def pago_masivo(self, data):
        if data:
            referencia = data['referencia']
            facturas = self.env['account.invoice'].search([('origin', 'ilike', referencia),('state', '=','open')])
            if facturas:
                monto_total = 0.0
                for factura in facturas:
                    monto_total = monto_total + factura.amount_total

                monto = data['monto'].replace(',', '')

                amount = float(monto)
                payment_difference = float(monto) - monto_total

                date = datetime.now().date()
                fecha_format = "{:%d/%m/%y}".format(date)
                dia = fecha_format[0:2]
                mes = fecha_format[3:5]
                anho = fecha_format[6:10]
                fecha = anho+'/'+mes+'/'+dia

                data ={
                 'payment_type': 'inbound',
                 'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                 'partner_type': 'customer',
                 'partner_id': factura.partner_id.id,
                 'amount': amount,
                 'payment_difference' : payment_difference,
                 'currency_id': self.env['res.currency'].search([('name', '=', 'PEN')]).id,
                 'payment_date': fecha,
                 'journal_id': self.env['account.payment'].search([('code', '=', 'BNK1')], limit=1).id
                 }

                self.env['account.payment'].create(data)
                a=1






