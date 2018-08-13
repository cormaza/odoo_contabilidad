# -*- coding: utf-8 -*-

import time
import re
from odoo import api, models



class ReportBalanceComprobacion(models.AbstractModel):
    _name = 'report.biosis_cont_report.balance_comprobacion'

    def _compute_account_balance(self, company, accounts):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict((fn, 0.0) for fn in mapping.keys())
        if accounts:
            tables, where_clause, where_params = self.env['account.move.line'].with_context(company_id= company)._query_get()
            #tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def _compute_report_balance(self, company, reports):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(company, report.account_ids)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
                res[report.id]['account'] = self._compute_account_balance(company, accounts)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(company,report.account_report_id)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._compute_report_balance(company, report.children_ids)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
        return res

    def get_account_lines(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(data['used_context']['company'],child_reports)
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(data['used_context']['company'],child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * report.sign,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False, #used to underline the financial report balances
            }

            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign

            lines.append(vals)
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue

            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * report.sign or 0.0,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and 4,
                        'account_type': account.internal_type,
                    }



                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * report.sign
                        if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        new_lines = self._add_financial_columns(lines)
        return new_lines

    #Se añade las columnas necesarias para el reporte de balance
    # [codigo],[deudor],[acreedor]
    def _add_financial_columns(self,lines):
        lines_new = []
        for line in lines:
            if line['type'] == 'account':
                line['codigo'] = line['name'].split()[0]
            elif line['type'] == 'report':
                line['codigo'] = ''

            if line['balance'] > 0:
                line['deudor'] = line['balance']
                line['acreedor'] = 0
            else:
                line['acreedor'] = line['balance']*-1
                line['deudor'] = 0
            lines_new.append(line)
        lines_new1 = self._add_stock_result_columns(lines_new)
        return lines_new1

    def _add_stock_result_columns(self,lines):
        lines_new = []
        for line in lines:
            if line['type'] == 'account':
                codigo = line['codigo']
                pattern = re.compile("^[1-5]")
                pattern1 = re.compile("^6")
                pattern2 = re.compile("^[7-9]")
                pattern3 = re.compile("^79")
                pattern4 = re.compile("^69")
                pattern5 = re.compile("^70")
                pattern6 = re.compile("^61")
                if pattern.match(codigo):
                    line['tc_debe'] = 0
                    line['tc_haber'] = 0
                    line['activo'] = line['deudor']
                    line['pasivo'] = line['acreedor']
                    line['perdida'] = 0
                    line['ganancia'] = 0
                    line['perdida1'] = 0
                    line['ganancia1'] = 0
                elif pattern1.match(codigo):
                    line['tc_debe'] = 0
                    line['tc_haber'] = 0
                    line['activo'] = 0
                    line['pasivo'] = 0
                    line['perdida'] = line['deudor']
                    line['ganancia'] = line['acreedor']
                    line['perdida1'] = 0
                    line['ganancia1'] = 0
                elif pattern2.match(codigo):
                    line['tc_debe'] = 0
                    line['tc_haber'] = 0
                    line['activo'] = 0
                    line['pasivo'] = 0
                    line['perdida'] = 0
                    line['ganancia'] = 0
                    line['perdida1'] = line['deudor']
                    line['ganancia1'] = line['acreedor']
                elif pattern6.match(codigo):
                    line['tc_debe'] = line['deudor']
                    line['tc_haber'] = line['acreedor']
                    line['activo'] = 0
                    line['pasivo'] = 0
                    line['perdida'] = 0
                    line['ganancia'] = 0
                    line['perdida1'] = 0
                    line['ganancia1'] = 0

                 #Cuenta 79 NO APARECE EN NINGUNA
                if pattern3.match(codigo):
                    line['tc_debe'] = 0
                    line['tc_haber'] = 0
                    line['activo'] = 0
                    line['pasivo'] = 0
                    line['perdida'] = 0
                    line['ganancia'] = 0
                    line['perdida1'] = 0
                    line['ganancia1'] = 0

                 #Cuenta 69 APARECE EN AMBOS
                if pattern4.match(codigo):
                    line['tc_debe'] = line['deudor']
                    line['tc_haber'] = line['acreedor']
                    line['activo'] = 0
                    line['pasivo'] = 0
                    line['perdida'] = line['deudor']
                    line['ganancia'] = line['acreedor']
                    line['perdida1'] = line['deudor']
                    line['ganancia1'] = line['acreedor']

                # Cuenta 70 APARECE EN AMBOS
                if pattern5.match(codigo):
                    line['tc_debe'] = 0
                    line['tc_haber'] = 0
                    line['activo'] = 0
                    line['pasivo'] = 0
                    line['perdida'] = line['deudor']
                    line['ganancia'] = line['acreedor']
                    line['perdida1'] = line['deudor']
                    line['ganancia1'] = line['acreedor']

            elif line['type'] == 'report':
                line['debit'] = 0
                line['credit'] = 0
                line['tc_debe'] = 0
                line['tc_haber'] = 0
                line['activo'] = 0
                line['pasivo'] = 0
                line['deudor'] = 0
                line['acreedor'] = 0
                line['balance'] = 0
                line['perdida'] = 0
                line['ganancia'] = 0
                line['perdida1'] = 0
                line['ganancia1'] = 0
            lines_new.append(line)
        return lines_new


    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_lines = self.get_account_lines(data.get('form'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_account_lines': report_lines,
        }
        return self.env['report'].render('biosis_cont_report.report_balance_comprobacion', docargs)
