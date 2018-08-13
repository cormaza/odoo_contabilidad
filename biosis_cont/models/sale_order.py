# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
import bs4, urllib2, urllib
from datetime import datetime, date

class SaleOrder(models.Model):
    _inherit = "sale.order"

    via = fields.Selection([
        ('A',u'Aéreo'),
        ('M',u'Marítimo')
    ], string=u'Vía', required=True, default="A")
    actividad = fields.Selection([
        ('E',u'Exportación'),
        ('I',u'Importación')
    ], string=u'Actividad', required=True, default="E")
    tipo = fields.Selection([
        ('FCL',u'Full Container Load'),
        ('LCL',u'Less Container Load')
    ], string=u'Tipo', required=True, default="FCL")
    linea_id = fields.Many2one('sale.linea', string=u'Linea')
    deposito_id = fields.Many2one('sale.deposito', string=u'Depósito')
    vacio_id = fields.Many2one('sale.vacio', string=u'Vacio')
    tipo_vacio_id = fields.Many2one('sale.tipo.vacio', string=u'Tipo Vacio')
    agente_aduana_id = fields.Many2one('sale.agente.aduana', string=u'Agente de Aduana')
    agente_portuario_id = fields.Many2one('sale.agente.portuario', string=u'Agente Portuario')
    #valor_tipo_cambio = fields.Float(string=u'Valor tipo Cambio', store=True, digits=(4, 3))

    # @api.multi
    # @api.onchange('date_order')
    # def onchange_date_order(self):
    #     # mes = "05"
    #     # anho = "2016"
    #     # web = urllib2.urlopen('http://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias')
    #     valor_compra = 0
    #     valor_venta = 0
    #     sw = 0
    #     # self.invoice_line_ids = {}
    #     value_tipo_cambio = 'V'
    #     if value_tipo_cambio == 'V' or value_tipo_cambio == 'C':
    #         self.invoice_line_ids = {}
    #         fecha = self.date_order
    #         if fecha != False:
    #             dia = fecha[8:10]
    #             mes = fecha[5:7]
    #             anho = fecha[0:4]
    #             fecha_sist = datetime.now().date()
    #
    #             # fecha_hoy = str(fecha_sist.year)+'-'+str(fecha_sist.month)+'-'+str(fecha_sist.day)
    #             fecha_comprobante = datetime.strptime(str(int(anho))+'-'+str(int(mes))+'-'+str(int(dia)),"%Y-%m-%d").date()
    #
    #             if str(fecha_comprobante) > str(fecha_sist):
    #                 self.valor_tipo_cambio = 0
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
    #                             # print soup.prettify()
    #                             tabla = soup.find_all('table')[1]
    #                             # fila = tabla.find_all('tr')
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
    #                                                 sw = 0
    #                                             #else:
    #                                                 #sw = 1
    #                                         pos = pos + 1
    #
    #                                 if sw == 1:
    #                                     warning = {
    #                                         'title': _('Alerta!'),
    #                                         'message': _('No existe tipo de cambio para esta fecha!'),
    #                                     }
    #                                     return {'warning': warning}
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
    #                     if value_tipo_cambio == 'V':
    #                         value = round(float(valor_venta), 4)
    #                         self.valor_tipo_cambio = value
    #                     else:
    #                         if value_tipo_cambio == 'C':
    #                             value = round(float(valor_compra), 4)
    #                             self.valor_tipo_cambio = value
    #         else:
    #             value_tipo_cambio = 'N'
    #             warning = {
    #                 'title': _('Alerta!'),
    #                 'message': _('Debe seleccionar la fecha de Recibo!'),
    #             }
    #             return {'warning': warning}
    #     else:
    #         self.valor_tipo_cambio = 0
    #
    # #def get_tc_web(self, mes, anho, dia):
