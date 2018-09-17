# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date,timedelta
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

    venta = fields.Float(string=u'Valor Venta', digits=(4, 3),store=True)
    compra = fields.Float(string=u'Valor Compra', digits=(4, 3),store=True)

    def _get_timestamp(self):
        dt = datetime.now()
        lima = timezone('America/Lima')
        f = lima.localize(dt, is_dst=True)
        return f
        #return datetime.now(pytz.utc)

    name = fields.Datetime(string='Fecha', required=True, index=True,
                           default=_get_timestamp)

    @api.multi
    @api.onchange('name')
    def onchange_name(self):
        fecha = self.name
        valor_compra = 0
        valor_venta = 0
        if self.currency_id.id==False:
            moneda = self._context['currency_id.name']

        if self.currency_id.name == 'USD' or moneda=='USD':
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
                            valor_compra, valor_venta =  self.valor_compra_venta_standard(mes,anho)
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

                                    valor_compra, valor_venta = self.valor_compra_venta(dia,mes, anho)

                                    if valor_compra == 0 and valor_venta == 0:
                                        dia = int(dia) - 1
                                        valor_compra, valor_venta = self.valor_compra_venta(dia, mes, anho)

                                if valor_compra==0 or valor_venta==0: #En caso 30 de julio sea lunes,
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
                        self.compra= valor_compra
                        value = round(float(valor_venta), 4)
                        self.rate = 1/value

            else:
                warning = {
                    'title': _('Alerta!'),
                    'message': _('Debe seleccionar la fecha de Recibo!'),
                }
                return {'warning': warning}


    def url_sunat(self,mes,anho):
        return urllib2.urlopen("http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias?mes=" + mes + "&anho=" + anho + "")

    def valor_compra_venta(self,dia,mes,anho):
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
                pos = pos + 1

        return valor_compra,valor_venta

    def valor_compra_venta_standard(self,mes,anho):
        valor_compra = 0
        valor_venta = 0
        web = self.url_sunat(mes, anho)
        soup = bs4.BeautifulSoup(web, 'lxml')
        # soup.prettify()
        tabla = soup.find_all('table')[1]
        # fila = tabla.find_all('tr')
        valor_compra = tabla.find_all('td')[-2].text.strip()
        valor_venta = tabla.find_all('td')[-1].text.strip()
        return valor_compra,valor_venta


