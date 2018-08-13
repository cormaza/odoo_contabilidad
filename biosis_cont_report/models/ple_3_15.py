# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_15(models.Model):
    _name = 'account.ple.3.15'
    _description = u'LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LA CUENTA 37 ACTIVO DIFERIDO Y DE LA ' \
                   u'CUENTA 49 PASIVO DIFERIDO (PCGE)'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable', required=True)
    tipo_cpbt_4 = fields.Char(string=u'Tipo Comprobante', required=True)
    serie_cpbt_5 = fields.Char(string=u'Serie del Comprobante', default=u'-')
    numero_cpbt_6 = fields.Char(string=u'Número Comprobante', required=True)
    cod_cuenta_c_7 = fields.Char(string=u'Código de la cuenta contable asociada a la obligación', required=True)
    concepto_8 = fields.Char(string=u'Concepto o descripción de la operación')
    saldo_final_9 = fields.Char(string=u'Saldo Final', default=u'-')
    adicciones_10 = fields.Char(string=u'Adiciones', default=u'-')
    deducciones_11 = fields.Char(string=u'Deducciones', default=u'-')
    estado_12 = fields.Char(string=u'Estado', required=True)
    invoice_id = fields.Many2one('account.invoice', string=u'Documento relacionado')
