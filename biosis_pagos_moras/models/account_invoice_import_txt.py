# -*- coding: utf-8 -*-
from StringIO import StringIO
from datetime import datetime, date
from odoo import api, fields, models
import base64


class TxtImport(models.TransientModel):
    _name = 'account.invoice.import.txt'
    _description = u"Upload mora Txt "

    fichero = fields.Binary(u'Archivo CREP')

    @api.multi
    def procesar_txt(self):
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
            self.crear_boleta_mora(datos)


    @api.multi
    def crear_boleta_mora(self, data):
        if data:
            referencia = data['referencia']
            facturas = self.env['account.invoice'].search([('origin', 'ilike', referencia),('state', '=','open')])
            if facturas:
                monto_total = 0.0
                for factura in facturas:
                    monto_total = monto_total + factura.amount_total
                #self.generar_boleta(factura, data['monto'], monto_total)

    @api.multi
    def generar_boleta(self, invoice, monto_txt, monto_total):
        conteo = 0
        boleta_id = self.env['einvoice.catalog.01'].search([('code', '=', '01')]).id
        serie_id = self.env['biosis.facturacion.einvoice.serie'].search([('alfanumerico', '=', 'F002')]).id
        # serie_id = self.env['biosis.facturacion.einvoice.serie'].search([('alfanumerico', '=', 'F002'),
        #                                                                  ('company_id', '=', invoice.company_id.id)]).id
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
            monto = monto_txt.replace(',', '')
            line2.price_unit = float(monto) - monto_total
            descripcion = line2.name
            line2.name= u'Interés moratorio ' + descripcion
            line2.invoice_line_tax_ids = {}
            line2.write({'invoice_id': fact.id})
        return fact




