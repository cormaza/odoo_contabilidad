# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_16_1(models.Model):
    _name = 'account.ple.3.16.1'
    _description = u'LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LA CUENTA 50 - CAPITAL '

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    importe_capital_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    valor_nominal_3 = fields.Char(string=u'Valor nominal por acción o participación social', required=True)
    num_acc_sus_4 = fields.Char(string=u'Número de acciones o participaciones sociales suscritas', required=True)
    num_acc_pag_5 = fields.Char(string=u'Número de acciones o participaciones sociales pagadas', default=u'-')
    estado_6 = fields.Char(string=u'Estado', required=True)
    ##invoice_id = fields.Many2one('account.invoice', string=u'Documento relacionado')
