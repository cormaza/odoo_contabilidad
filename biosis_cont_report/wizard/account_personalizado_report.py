# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, datetime

class AccountPersonalizado(models.TransientModel):
    _name = "account.personalizado"
    _description = "Reporte Personalizado"

    date_from = fields.Date(string='Desde:')
    date_to = fields.Date(string='Hasta:')
    journal_ids = fields.Many2many('account.journal', string=u'Diario', required=True)
    digits = fields.Selection([('2', u'2 digitos'),
                                ('3', u'3 digitos'),
                                ('4', u'4 digitos'),
                                ('5', u'5 digitos'),
                                ('6', u'6 digitos')], string=u'Cantidad digitos:')

    # Metodo para crear xlsx
    @api.multi
    def print_report_xls(self):
        nombre_reporte = u'Reporte Personalizado para Diarios'
        report_balance = self.env['account.financial.report'].search([
            ('name','=',u'Balance de Comprobación')
        ])
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'digits','journal_ids'])[0]
        data['form']['debit_credit'] = True
        data['form']['account_report_id'] = (report_balance.id,report_balance.name)
        data['form']['enable_filter'] = False
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return {'type': 'ir.actions.report.xml',
                'report_name': 'biosis_cont_report.report_personalizado_xls.xlsx',
                'datas': data['form'],
                'name': nombre_reporte
                }

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'posted'
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result