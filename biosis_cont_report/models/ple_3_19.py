# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_19(models.Model):
    _name = 'account.ple.3.19'
    _description = u'LIBRO DE INVENTARIOS Y BALANCES - ESTADO DE CAMBIOS EN EL PATRIMONIO NETO'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cod_catalog_2 = fields.Char(string=u'Código del catálogo', required=True)
    cod_rubro_3 = fields.Char(string=u'Código del Rubro del Estado Financiero', required=True)
    capital_4 = fields.Char(string=u'Saldo del Rubro Contable', required=True)
    acc_inversion_5 = fields.Char(string=u'Acciones de Inversión', required=True)
    capital_adic_6 = fields.Char(string=u'Capital Adicional', required=True)
    result_no_realizados_7 = fields.Char(string=u'Resultados no Realizados', required=True)
    reservas_leg_8 = fields.Char(string=u'Reservas Legales', required=True)
    otras_reservas_9 = fields.Char(string=u'Otras reservas', required=True)
    result_acumulados_10 = fields.Char(string=u'Resultados Acumulados', required=True)
    dif_conversion_11 = fields.Char(string=u'Diferencias de Conversión', required=True)
    ajustes_patrimonio_12 = fields.Char(string=u'Ajustes al Patrimonio', required=True)
    result_ejer_neto_13 = fields.Char(string=u'Resultado Neto del Ejercicio', required=True)
    excdte_reval_14 = fields.Char(string=u'Excedente de Revaluación', required=True)
    result_ejer_15 = fields.Char(string=u'Resultado del Ejercicio', required=True)
    estado_16 = fields.Char(string=u'Estado', required=True)
