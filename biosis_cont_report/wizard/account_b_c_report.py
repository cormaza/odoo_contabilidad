# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountingReportBalanceComprobacion(models.TransientModel):
    _name = "account.balancecomprobacion"
    _inherit = "account.common.report"
    _description = u"Reporte de Balance de Comprobación"

    @api.model
    def _get_account_report(self):
        reports = []
        if self._context.get('active_id'):
            menu = self.env['ir.ui.menu'].browse(self._context.get('active_id')).name
            reports = self.env['account.financial.report'].search([('name', 'ilike', menu)])
        return reports and reports[0] or False

    enable_filter = fields.Boolean(string=u'Habilitar comparación')
    account_report_id = fields.Many2one('account.financial.report', string='Reportes Contables', required=True, default=_get_account_report)
    label_filter = fields.Char(string='Etiqueta de columna', help="This label will be displayed on report to show the balance computed for the given comparison filter.")
    filter_cmp = fields.Selection([('filter_no', 'Sin filtros'), ('filter_date', 'Fecha')], string='Filtrar por', required=True, default='filter_no')
    date_from_cmp = fields.Date(string='Fecha Inicio')
    date_to_cmp = fields.Date(string='Fecha Fin')
    debit_credit = fields.Boolean(string=u'Mostrar columnas de débito/crédito', help="This option allows you to get more details about the way your balances are computed. Because it is space consuming, we do not allow to use it while doing a comparison.")

    def _build_comparison_context(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        if data['form']['filter_cmp'] == 'filter_date':
            result['date_from'] = data['form']['date_from_cmp']
            result['date_to'] = data['form']['date_to_cmp']
            result['strict_range'] = True
        return result

    @api.multi
    def check_report(self):
        res = super(AccountingReportBalanceComprobacion, self).check_report()
        data = {}
        data['form'] = self.read(['account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move'])[0]
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        res['data']['form']['comparison_context'] = comparison_context
        return res

    #Metodo para crear xlsx
    @api.multi
    def print_report_xls(self):
        #reporte_balance = self.env['report.biosis_cont.report_balance_comprobacion']
        res = super(AccountingReportBalanceComprobacion, self).check_report()
        data = {}
        data['form'] = self.read(['account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move'])[0]
        #for field in ['account_report_id']:
        #    if isinstance(data['form'][field], tuple):
        #        data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        res['data']['form']['comparison_context'] = comparison_context
        return {'type': 'ir.actions.report.xml',
                'report_name': 'biosis_cont_report.balance_comprobacion_xls.xlsx',
                'datas': res['data']['form'],
                'name': u'Balance de Comprobación'
                }

    def _print_report(self, data):
        data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0])
        #Llama a la clase con name "report.biosis_cont_report.balance_comprobacion", para crear reporte
        return self.env['report'].get_action(self, 'biosis_cont_report.report_balance_comprobacion', data=data)
