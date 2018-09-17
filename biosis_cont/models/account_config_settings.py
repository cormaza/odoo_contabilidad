# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'
    #itf_account = fields.Many2one('account.account',string=u'Cuenta para ITF')
    #itf_porcentaje = fields.Float(string=u'Porcentaje para ITF')
    #comisiones_account = fields.Many2one('account.account',string=u'Cuenta para Comisiones')
    #comisiones_porcentaje = fields.Float(string=u'Porcentaje para Comisiones')
    def _get_company(self):
        return self.company_id


    liquidacion = fields.Boolean('Aplicar liquidacion en facturas',
                                 implied_group='purchase.group_analytic_accounting',
        help="Permite aplicar liquidacion en las factura de compra.")

    detraccion = fields.Selection([('DO', 'Una sola cuenta'), ('DM', 'Varias cuentas')],
                                     required=True)

    diario_detraccion = fields.Many2one('account.journal', string='Diario',
                                        domain=[('type', '=', 'bank')])

    @api.multi
    @api.onchange('detraccion')
    def onchange_detraccion(self):
        if self.detraccion == 'DM':
            self.diario_detraccion = {}

    @api.onchange('company_id')
    def onchange_company_id(self):
        # update related fields
        self.currency_id = False
        if self.company_id:
            company = self.company_id
            self.chart_template_id = company.chart_template_id
            self.has_chart_of_accounts = len(company.chart_template_id) > 0 or False
            self.expects_chart_of_accounts = company.expects_chart_of_accounts
            self.currency_id = company.currency_id
            self.transfer_account_id = company.transfer_account_id
            self.company_footer = company.rml_footer
            self.tax_calculation_rounding_method = company.tax_calculation_rounding_method
            self.bank_account_code_prefix = company.bank_account_code_prefix
            self.cash_account_code_prefix = company.cash_account_code_prefix
            self.code_digits = company.accounts_code_digits

            # update taxes
            ir_values = self.env['ir.values']
            taxes_id = ir_values.get_default('product.template', 'taxes_id', company_id=self.company_id.id)
            supplier_taxes_id = ir_values.get_default('product.template', 'supplier_taxes_id',
                                                      company_id=self.company_id.id)
            self.default_sale_tax_id = isinstance(taxes_id, list) and len(taxes_id) > 0 and taxes_id[0] or taxes_id
            self.default_purchase_tax_id = isinstance(supplier_taxes_id, list) and len(supplier_taxes_id) > 0 and \
                                           supplier_taxes_id[0] or supplier_taxes_id
            self.config_get_detraccion(company.id)
        return {}

    def config_get_detraccion(self,company_id):
        config_det = self.env['account.config.settings'].search(
            [('company_id', '=', company_id)],order='id desc',limit=1)
        self.detraccion = config_det.detraccion
        diario_detraccion = config_det.diario_detraccion
        # if diario_detraccion.id != False:
        #     diario = self.env['account.journal'].search([('id', '=', diario_detraccion)],limit=1)
        # else:
        #     diario = diario_detraccion
        self.diario_detraccion = diario_detraccion



