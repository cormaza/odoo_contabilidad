# -*- coding: utf-8 -*-
import datetime
import calendar
from odoo import api, fields, models, _

class AccountLiquidacionLine(models.Model):
    _inherit = 'account.invoice.line'
    _description = u'Lina de Pago - Liquidación'

    fecha_emision = fields.Date(string=u'Fecha Emisión')
    emisor = fields.Char(string=u'Emisor')

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        super(AccountLiquidacionLine, self)._compute_price()
        if self.invoice_id.is_liquidacion == True:
            if self.invoice_id.servicio_id.property_account_expense_id:
                self.account_id = self.invoice_id.servicio_id.property_account_expense_id
            else:
                self.account_id = self.invoice_id.servicio_id.categ_id.property_account_expense_categ_id


