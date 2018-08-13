# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, datetime

class AccountCuentasCP(models.TransientModel):
    _name = "account.cuentascp"
    _description = "Reporte de Cuentas Cobrar/Pagar"

    date_desde = fields.Date(string='Desde:')
    date_hasta = fields.Date(string='Hasta:')

    tipo_reporte = fields.Selection([('cpp', u'Cuentas por pagar'),
                                     ('cpc', u'Cuentas por cobrar')], string=u'Tipo de Reporte')

    # Metodo para crear xlsx
    @api.multi
    def print_report_xls(self):
        nombre_reporte = u'Reporte de Cuentas por '+(u'Cobrar' if self.tipo_reporte == 'cpc' else u'Pagar')
        data = {}
        data['form'] = self.read(['date_desde', 'date_hasta', 'tipo_reporte'])[0]
        return {'type': 'ir.actions.report.xml',
                'report_name': 'biosis_cont_report.report_cuentas_xls.xlsx',
                'datas': data['form'],
                'name': nombre_reporte
                }