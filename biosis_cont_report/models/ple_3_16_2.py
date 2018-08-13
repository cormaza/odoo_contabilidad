# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_16_2(models.Model):
    _name = 'account.ple.3.16.2'
    _description = u'LIBRO DE INVENTARIOS Y BALANCES -  ESTRUCTURA DE LA PARTICIPACIÓN ACCIONARIA O DE PARTICIPACIONES SOCIALES'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    tipo_doc_acc_2 = fields.Char(string=u'Tipo de Documento de Identidad del accionista o socio', required=True)
    numero_doc_acc_3 = fields.Char(string=u'Número de Documento de Identidad del accionista o socio', required=True)
    cod_tipo_acc_4 = fields.Char(string=u'Código de los tipos de acciones o participaciones', required=True)
    nombre_acc_5 = fields.Char(string=u'Apellidos y Nombres, Denominación o Razón Social del accionista o socio', default=u'-')
    cant_acc_6 = fields.Char(string=u'Número de acciones o de participaciones sociales', required=True)
    prcntj_acc_7 = fields.Char(string=u'Porcentaje Total de participación de acciones o participaciones sociales', required=True)
    estado_8 = fields.Char(string=u'Estado', required=True)
    ##invoice_id = fields.Many2one('account.invoice', string=u'Documento relacionado')