# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_14(models.Model):
    _name = 'account.ple.3.14'
    _description = u'LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LA CUENTA 47 - ' \
                   u'BENEFICIOS SOCIALES DE LOS TRABAJADORES (PCGR)'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable', required=True)
    tipo_doc_tra_4 = fields.Char(string=u'Tipo de Documento de Identidad del trabajador', default=u'')
    numero_doc_tra_5 = fields.Char(string=u'Número de Documento de Identidad del trabajador', default=u'')
    nombre_tra_7 = fields.Char(string=u'Apellidos y Nombres de trabajador', required=True)
    saldo_final_8 = fields.Char(string=u'Saldo Final', default=u'-')
    estado_9 = fields.Char(string=u'Estado', required=True)
    #invoice_id = fields.Many2one('account.invoice', string=u'Documento relacionado')
