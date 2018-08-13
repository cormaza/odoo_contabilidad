# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self, post_move=True):

        super(AccountAssetDepreciationLine, self).create_move()

        invoice_line_gastos_ids = []
        var = self.asset_id.invoice_id.invoice_line_ids
        if var:
            for linea in var:
                product_line = linea.product_id
                if product_line:
                    if product_line.asset_category_id:
                        invoice_line_gastos_ids.append(linea)

        if len(invoice_line_gastos_ids) > 0:
            created_moves = self.env['account.move']
            prec = self.env['decimal.precision'].precision_get('Account')
            for line2 in self:
               #asiento = line.f_destino(invoice_line_gastos_ids)
                depreciation_date = self.env.context.get(
                    'depreciation_date') or line2.depreciation_date or fields.Date.context_today(self)
                company_currency = line2.asset_id.company_id.currency_id
                current_currency = line2.asset_id.currency_id
                amount = current_currency.compute(line2.amount, company_currency)
                sign = (
                       line2.asset_id.category_id.journal_id.type == 'purchase' or line2.asset_id.category_id.journal_id.type == 'sale' and 1) or -1
                reference = line2.asset_id.code
                journal_id = line2.asset_id.category_id.journal_id.id
                partner_id = line2.asset_id.partner_id.id
                categ_type = line2.asset_id.category_id.type
                prec = self.env['decimal.precision'].precision_get('Account')

                cuentas_destino = []
                producto = line2.asset_id.invoice_id.invoice_line_ids.product_id
                price_unit_92 = 0.000
                price_unit_94 = 0.000
                price_unit_95 = 0.000
                price_unit_97 = 0.000
                price = 0.0
                a = 0
                b = 0
                c = 0
                d = 0

                if producto.account_92_id:
                    price_unit_92 = amount * (producto.porcentaje_92 / 100)
                    a = 1

                if producto.account_94_id:
                    price_unit_94 = amount * (producto.porcentaje_94 / 100)
                    b = 1
                if producto.account_95_id:
                    price_unit_95 = amount * (producto.porcentaje_95 / 100)
                    c = 1
                if producto.account_97_id:
                    price_unit_97 = amount * (producto.porcentaje_97 / 100)
                    d = 1

                if a == 1:
                    move_line_1 = {
                        'name': line2.asset_id.invoice_id.invoice_line_ids.product_id.account_92_id.name,
                        'account_id': line2.asset_id.invoice_id.invoice_line_ids.product_id.account_92_id.id,
                        'debit': price_unit_92,
                        'credit': 0.0,
                        'journal_id': journal_id,
                        'partner_id': partner_id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'amount_currency': company_currency != current_currency and - sign * line2.amount or 0.0,
                        'analytic_account_id': line2.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
                        'date': depreciation_date,
                    }
                    cuentas_destino.append((0,0,move_line_1))
                if b == 1:
                    move_line_2 = {
                        'name': line2.asset_id.invoice_id.invoice_line_ids.product_id.account_94_id.name,
                        'account_id': line2.asset_id.invoice_id.invoice_line_ids.product_id.account_94_id.id,
                        'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                        'debit': price_unit_94,
                        'journal_id': journal_id,
                        'partner_id': partner_id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'amount_currency': company_currency != current_currency and sign * line2.amount or 0.0,
                        'analytic_account_id': line2.asset_id.category_id.account_analytic_id.id if categ_type == 'purchase' else False,
                        'date': depreciation_date,
                    }
                    cuentas_destino.append((0, 0, move_line_2))

                if c == 1:
                    move_line_3 = {
                        'name': line2.asset_id.invoice_id.invoice_line_ids.product_id.account_95_id.name,
                        'account_id': line2.asset_id.invoice_id.invoice_line_ids.product_id.account_95_id.id,
                        'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                        'debit': price_unit_95,
                        'journal_id': journal_id,
                        'partner_id': partner_id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'amount_currency': company_currency != current_currency and sign * line2.amount or 0.0,
                        'analytic_account_id': line2.asset_id.category_id.account_analytic_id.id if categ_type == 'purchase' else False,
                        'date': depreciation_date,
                    }
                    cuentas_destino.append((0, 0, move_line_3))
                if d == 1:
                    move_line_4 = {
                        'name': line2.asset_id.invoice_id.invoice_line_ids.product_id.account_97_id.name,
                        'account_id': line2.asset_id.invoice_id.invoice_line_ids.product_id.account_97_id.id,
                        'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                        'debit': price_unit_97,
                        'journal_id': journal_id,
                        'partner_id': partner_id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'amount_currency': company_currency != current_currency and sign * line2.amount or 0.0,
                        'analytic_account_id': line2.asset_id.category_id.account_analytic_id.id if categ_type == 'purchase' else False,
                        'date': depreciation_date,
                    }
                    cuentas_destino.append((0, 0, move_line_4))


                # Cuenta imputable de costos y gastos
                cuenta_79 = self.env['account.account'].search([('code', '=like', '791%')], limit=1)
                move_line_5 = {
                    'name': cuenta_79.name,
                    'account_id': cuenta_79.id,
                    'credit': amount,
                    'debit': 0.0,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and sign * line2.amount or 0.0,
                    'analytic_account_id': line2.asset_id.category_id.account_analytic_id.id if categ_type == 'purchase' else False,
                    'date': depreciation_date,
                }
                cuentas_destino.append((0, 0, move_line_5))

                move_vals = {
                    'ref': reference,
                    'date': depreciation_date or False,
                    'journal_id': line2.asset_id.category_id.journal_id.id,
                    'line_ids': cuentas_destino,
                    'asset_id': line2.asset_id.id,
                }
                move = self.env['account.move'].create(move_vals)
                line2.write({'move_id': move.id, 'move_check': True})
                created_moves |= move

            if post_move and created_moves:
                created_moves.filtered(
                    lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
            return [x.id for x in created_moves]






class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    #porcentaje_annual = fields.Float(related='category_id.porcentaje_anual',string='Porcentaje Anual/Depreciacion Anual')
    #related='category_id.porcentaje_anual',
    #default='category_id.porcentaje_anual'
    porcentaje_annual = fields.Float(related='category_id.porcentaje_anual',string='Porcentaje Anual/Depreciacion Anual')
    #porcentaje_amortizacion = fields.Float(string='Porcentaje Amortizacion/Depreciacion mensual',  digits=(3,2))
    #related='category_id.method_percentage',
    porcentaje_amortizacion = fields.Float(related='category_id.method_percentage',string='Porcentaje Amortizacion/Depreciacion mensual')
    #,default='category_id.method_percentage'

    @api.multi
    def compute_depreciation_board(self):
        super(AccountAssetAsset, self).compute_depreciation_board()
        precision = self.env['decimal.precision'].precision_get('Account')
        for asset in self:
            if asset.depreciation_line_ids:
                last_depr = asset.depreciation_line_ids[-1]
                if not last_depr.move_id and float_is_zero(
                        last_depr.amount, precision):
                    last_depr.unlink()
            if asset.move_end_period:
                # Reescribir la fecha de la depreciación
                depr_lin_obj = self.env['account.asset.depreciation.line']
                new_depr_lines = depr_lin_obj.search(
                    [('asset_id', '=', asset.id), ('move_id', '=', False)])
                # En el caso de que la fecha de última amortización no sea
                # la de compra se debe generar el cuadro al período siguiente
                depreciation_date = fields.Date.from_string(
                    asset._get_last_depreciation_date()[asset.id])
                nb = 0
                for depr_line in new_depr_lines:
                    depr_date = fields.Date.from_string(
                        depr_line.depreciation_date)
                    if asset.method_period == 12:
                        depr_date = depr_date.replace(depr_date.year, 12, 31)
                    else:
                        if not asset.prorata:
                            if depr_date.day != 1:
                                depr_date = depreciation_date + relativedelta(
                                    months=+ (asset.method_period * (nb + 1)))
                            else:
                                depr_date = depreciation_date + relativedelta(
                                    months=+ (asset.method_period * nb))
                            nb += 1
                        last_month_day = calendar.monthrange(
                            depr_date.year, depr_date.month)[1]
                        depr_date = depr_date.replace(
                            depr_date.year, depr_date.month, last_month_day)
                    depr_line.depreciation_date = fields.Date.to_string(
                        depr_date)
        return True

    def _compute_board_amount(self, sequence, residual_amount, amount_to_depr,
                                  undone_dotation_number,
                                  posted_depreciation_line_ids, total_days,
                                  depreciation_date):


            if self.method_time == 'percentage':
                # Nuevo tipo de cálculo
                if sequence == undone_dotation_number:
                    return residual_amount
                else:
                    if sequence == 1 and self.prorata:
                        if self.method_period == 1:
                            total_days = calendar.monthrange(
                                depreciation_date.year, depreciation_date.month)[1]
                            days = total_days - float(depreciation_date.day) + 1
                        else:
                            days = (total_days - float(
                                depreciation_date.strftime('%j'))) + 1
                        percentage = self.category_id.method_percentage * days / total_days
                    else:
                        percentage = self.category_id.method_percentage
                    return amount_to_depr * percentage / 100
            elif (self.method == 'linear' and self.prorata and
                          sequence != undone_dotation_number):
                # Caso especial de cálculo que cambia
                # Debemos considerar también las cantidades ya depreciadas
                depreciated_amount = 0
                depr_lin_obj = self.env['account.asset.depreciation.line']
                for line in depr_lin_obj.browse(posted_depreciation_line_ids):
                    depreciated_amount += line.amount
                amount = (amount_to_depr + depreciated_amount) \
                         / self.method_number

                if sequence == 1:
                    if self.method_period == 1:
                        total_days = calendar.monthrange(
                            depreciation_date.year, depreciation_date.month)[1]
                        days = total_days - float(depreciation_date.day) + 1
                    else:
                        days = (total_days -
                                float(depreciation_date.strftime('%j'))) + 1
                    amount *= days / total_days
                return amount
            else:
                return super(AccountAssetAsset, self)._compute_board_amount(
                    sequence, residual_amount, amount_to_depr,
                    undone_dotation_number, posted_depreciation_line_ids,
                    total_days, depreciation_date)


    def _compute_board_undone_dotation_nb(self, depreciation_date, total_days):
        if self.method_time == 'percentage':
            number = 0
            percentage = 100.0
            while percentage > 0:
                if number == 0 and self.prorata:
                    days = (total_days -
                            float(depreciation_date.strftime('%j'))) + 1
                    percentage -= self.category_id.method_percentage * days / total_days
                else:
                    percentage -= self.category_id.method_percentage
                number += 1
            return number
        else:
            return super(AccountAssetAsset, self). \
                _compute_board_undone_dotation_nb(
                depreciation_date, total_days)


