# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountingReportCuentas(models.TransientModel):
    _name = "biosis_cont.report.cuentas"
    _inherit = "account.common.report"
    _description = u"Reporte de Balance de Comprobación"

    tipo_reporte = fields.Selection([('cpp',u'Cuentas por pagar'),
                                     ('cpc',u'Cuentas por cobrar')],string=u'Tipo de Reporte')
    @api.model
    def _get_account_report(self):
        reports = []
        if self._context.get('active_id'):
            menu = self.env['ir.ui.menu'].browse(self._context.get('active_id')).name
            reports = self.env['account.financial.report'].search([('name', 'ilike', menu)])
        return reports and reports[0] or False

    def _build_comparison_context(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        return result

    @api.multi
    def check_report(self):
        res = super(AccountingReportCuentas, self).check_report()
        data = {}
        data['form'] = \
        self.read(['account_report_id', 'date_from', 'date_to', 'journal_ids',  'target_move'])[0]
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        res['data']['form']['comparison_context'] = comparison_context
        return res

    # Metodo para crear xlsx
    @api.multi
    def print_report_xls(self):
        res = super(AccountingReportCuentas, self).check_report()
        data = {}
        data['form'] = self.read(
            ['account_report_id', 'date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        # for field in ['account_report_id']:
        #    if isinstance(data['form'][field], tuple):
        #        data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        res['data']['form']['comparison_context'] = comparison_context
        return {'type': 'ir.actions.report.xml',
                'report_name': 'biosis_cont.report_cuentas_xls.xlsx',
                'datas': res['data']['form'],
                'name': u'Reporte Cuentas'
                }

    def _print_report(self, data):
        data['form'].update(self.read(
            ['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter',
             'label_filter', 'target_move'])[0])
        return self.env['report'].get_action(self, 'biosis_cont.report_balance_comprobacion', data=data)