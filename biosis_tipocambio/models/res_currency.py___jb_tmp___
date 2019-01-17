# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import datetime, date, timedelta
from dateutil import parser
import bs4
import urllib2
import json
import math
import re
import time
import pytz
from pytz import timezone

from odoo import api, fields, models, tools, _

CURRENCY_DISPLAY_PATTERN = re.compile(r'(\w+)\s*(?:\((.*)\))?')


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    # def _get_timestamp(self):
    #     datos = self.env['res.currency.rate'].search([])
    #     for data in datos:
    #         if data:
    #             data.nombre =
    #             b=1
    #
    #     dt = datetime.now()
    #     # .    strftime('%Y-%m-%d 00:00:01')
    #     lima = timezone('America/Lima')
    #     f = lima.localize(dt, is_dst=True)
    #     return f
    nombre = fields.Date(string=u'Fecha', required=True, index=True)
    venta = fields.Float(string=u'Valor Venta', digits=(4, 3), store=True)
    compra = fields.Float(string=u'Valor Compra', digits=(4, 3), store=True)

    @api.multi
    def cron_tipo_cambio(self):
        cron = self.env['ir.cron'].search([
            ('model', 'ilike', 'res.currency.rate'),
            ('function', 'ilike', 'cron_tipo_cambio')]).nextcall

        fecha_cron = (datetime.strptime(cron, '%Y-%m-%d %H:%M:%S')).date()
        fecha_hoy = datetime.now().date()
        if str(fecha_cron) >= str(fecha_hoy):
            date_time1 = (datetime.now()).strftime('%Y-%m-%d 00:00:00')
            # date_hoy = (datetime.now()).strftime('%Y-%m-%d 05:00:01')
            date_time2 = datetime.strptime(date_time1, "%Y-%m-%d %H:%M:%S")
            # date_hoy2 = datetime.strptime(date_hoy, "%Y-%m-%d %H:%M:%S")
            lima = timezone('America/Lima')
            # fec = lima.localize(date_time2, is_dst=True)
            # fec = date_time2 + timedelta(hours=5)
            fec = date_time2

            # self.currency_id = self.env.ref("base.USD").id
            currency_id = self.env.ref("base.USD")
            fecha = date_time2.date()
            res = self.env['res.currency.rate'].search([('nombre', 'ilike', fecha)])

            if len(res) == 0:
                rate = self.tipo_cambio_usd(currency_id, date_time2)
                currency_rate = self.env['res.currency.rate'].create({'name': fec,
                                                                      'nombre': fec.date(),
                                                                      'venta': rate[0],
                                                                      'compra': rate[1],
                                                                      'rate': rate[2],
                                                                      'currency_id': currency_id.id})
                return currency_rate
            else:
                pass

    # @api.multi
    # def write(self):
    #     vals = {}
    #
    #     date_tmp = "Indefinido"
    #     if 'name' in vals:
    #         date_tmp = str(vals['name'])[:7].replace("-", "/")
    #
    #     if self.name:
    #         date_tmp = str(self.name)[:7].replace("-", "/")
    #     vals['period_name'] = date_tmp
    #     t = super(CurrencyRate, self).write(vals)
    #
    #     return t


    def tipo_cambio(self):
        fecha = self.nombre
        valor_compra = 0
        valor_venta = 0
        if self.currency_id.id == False:
            moneda = self._context['currency_id.name']

        if self.currency_id.name == 'USD' or moneda == 'USD':
            if fecha != False:
                dia = fecha[8:10]
                mes = fecha[5:7]
                anho = fecha[0:4]
                fecha_sist = datetime.now().date()
                solo_fecha = date(int(anho), int(mes), int(dia))
                if str(solo_fecha) > str(fecha_sist):
                    warning = {
                        'title': _('Alerta!'),
                        'message': _('No hay tipo de cambio para esta fecha!'),
                    }
                    return {'warning': warning}

                else:
                    fec = date(int(anho), int(mes), int(dia))
                    dia_semana = fec.weekday()
                    mes_num = fec.month

                    if dia_semana == 6 or dia_semana == 0:  # Comparamos si el dia de semana es domingo o lunes
                        if int(dia) == 1 and int(mes) == 1:
                            anho = str(int(anho) - 1)
                            mes = '12'
                            valor_compra, valor_venta = self.valor_compra_venta_standard(mes, anho)
                        else:
                            if dia_semana == 0 and int(dia) == 2:
                                mes = int(mes) - 1
                                if mes < 10:
                                    mes = '0' + str(mes)
                                valor_compra, valor_venta = self.valor_compra_venta_standard(mes, anho)
                            else:
                                if int(dia) == 1:
                                    mes = int(mes) - 1
                                    if mes < 10:
                                        mes = '0' + str(mes)
                                    valor_compra, valor_venta = self.valor_compra_venta_standard(mes, anho)
                                else:
                                    if dia_semana == 6:
                                        dia = int(dia) - 1
                                    else:
                                        if dia_semana == 0:
                                            dia = int(dia) - 2

                                    valor_compra, valor_venta = self.valor_compra_venta(dia, mes, anho)

                                    if valor_compra == 0 and valor_venta == 0:
                                        dia = int(dia) - 1
                                        valor_compra, valor_venta = self.valor_compra_venta(dia, mes, anho)

                                if valor_compra == 0 or valor_venta == 0:  # En caso 30 de julio sea lunes,
                                    # se obtiene dos días antes, pero como 28 es feriado, se obtiene del 27 de julio
                                    if dia_semana == 0:
                                        dia = int(dia) - 3
                                        valor_compra, valor_venta = self.valor_compra_venta(dia, mes, anho)

                    else:
                        valor_compra, valor_venta = self.valor_compra_venta(dia, mes, anho)

                    if valor_compra == 0 and valor_venta == 0:
                        warning = {
                            'title': _('Alerta!'),
                            'message': _('No hay tipo de cambio para esta fecha!'),
                        }
                        return {'warning': warning}
                    else:
                        value_v = round(float(valor_venta), 4)
                        self.venta = value_v
                        self.compra = valor_compra
                        name = self.nombre
                        self.name = name
                        # self.nombre = valor_compra
                        value = round(float(valor_venta), 4)
                        self.rate = 1 / value
                        # self.create()
                        return

            else:
                warning = {
                    'title': _('Alerta!'),
                    'message': _('Debe seleccionar la fecha de Recibo!'),
                }
                return {'warning': warning}

    # def create(self):
    #     a=2



    def tipo_cambio_usd(self, currency, fec):
        fech = fec
        valor_compra = 0
        valor_venta = 0
        if currency.id != False:
            moneda = currency.name

        if moneda == 'USD':
            if fech != False:
                fecha = str(fech.date())
                dia = fecha[8:10]
                mes = fecha[5:7]
                anho = fecha[0:4]
                fecha_sist = datetime.now().date()
                solo_fecha = date(int(anho), int(mes), int(dia))
                if str(solo_fecha) > str(fecha_sist):
                    warning = {
                        'title': _('Alerta!'),
                        'message': _('No hay tipo de cambio para esta fecha!'),
                    }
                    return {'warning': warning}

                else:
                    fec = date(int(anho), int(mes), int(dia))
                    dia_semana = fec.weekday()
                    mes_num = fec.month

                    if dia_semana == 6 or dia_semana == 0:  # Comparamos si el dia de semana es domingo o lunes
                        if int(dia) == 1 and int(mes) == 1:
                            anho = str(int(anho) - 1)
                            mes = '12'
                            valor_compra, valor_venta = self.valor_compra_venta_standard(mes, anho)
                        else:
                            if dia_semana == 0 and int(dia) == 2:
                                mes = int(mes) - 1
                                if mes < 10:
                                    mes = '0' + str(mes)
                                valor_compra, valor_venta = self.valor_compra_venta_standard(mes, anho)
                            else:
                                if int(dia) == 1:
                                    mes = int(mes) - 1
                                    if mes < 10:
                                        mes = '0' + str(mes)
                                    valor_compra, valor_venta = self.valor_compra_venta_standard(mes, anho)
                                else:
                                    if dia_semana == 6:
                                        dia = int(dia) - 1
                                    else:
                                        if dia_semana == 0:
                                            dia = int(dia) - 2

                                    valor_compra, valor_venta = self.valor_compra_venta(dia, mes, anho)

                                    if valor_compra == 0 and valor_venta == 0:
                                        dia = int(dia) - 1
                                        valor_compra, valor_venta = self.valor_compra_venta(dia, mes, anho)

                                if valor_compra == 0 or valor_venta == 0:  # En caso 30 de julio sea lunes,
                                    # se obtiene dos días antes, pero como 28 es feriado, se obtiene del 27 de julio
                                    if dia_semana == 0:
                                        dia = int(dia) - 3
                                        valor_compra, valor_venta = self.valor_compra_venta(dia, mes, anho)

                    else:
                        valor_compra, valor_venta = self.valor_compra_venta_standard(mes, anho)

                    if valor_compra == 0 and valor_venta == 0:
                        warning = {
                            'title': _('Alerta!'),
                            'message': _('No hay tipo de cambio para esta fecha!'),
                        }
                        return {'warning': warning}
                    else:
                        data = []
                        value_v = round(float(valor_venta), 4)
                        value_c = round(float(valor_compra), 4)
                        # self.venta = value_v
                        # self.compra = valor_compra
                        value = round(float(valor_venta), 4)
                        # self.rate = 1 / value
                        rate = 1 / value
                        data.append(value_v)
                        data.append(value_c)
                        data.append(rate)

                        return data

            else:
                warning = {
                    'title': _('Alerta!'),
                    'message': _('Debe seleccionar la fecha de Recibo!'),
                }
                return {'warning': warning}

    #
    # @api.model
    # def create(self, vals):
    #     a = 1
    #     res = super(CurrencyRate, self).create(vals)
    #
    #     b = 1

    @api.multi
    @api.onchange('nombre')
    def onchange_nombre(self):
        self.tipo_cambio()

    def url_sunat(self, mes, anho):
        return urllib2.urlopen("http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")

    def valor_compra_venta(self, dia, mes, anho):
        valor_compra = 0
        valor_venta = 0
        web = self.url_sunat(mes, anho)
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
                # else:
                #     valor_venta = col[pos].text.strip()
                #     valor_compra = col[pos - 1].text.strip()

                pos = pos + 1

        return valor_compra, valor_venta

    def valor_compra_venta_standard(self, mes, anho):
        valor_compra = 0
        valor_venta = 0
        web = self.url_sunat(mes, anho)
        soup = bs4.BeautifulSoup(web, 'lxml')
        # soup.prettify()
        tabla = soup.find_all('table')[1]
        # fila = tabla.find_all('tr')
        valor_compra = tabla.find_all('td')[-2].text.strip()
        valor_venta = tabla.find_all('td')[-1].text.strip()
        return valor_compra, valor_venta
