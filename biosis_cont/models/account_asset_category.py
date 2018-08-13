# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    porcentaje_anual = fields.Float(string=u'Porcentaje Anual', digits=(3, 2), default=0.0)
    # porcentaje_anuall = fields.Char(string='Annual depreciation percentage')

    @api.multi
    @api.onchange('porcentaje_anual')
    def onchange_porcentaje_anual(self):
        for asset in self:
            asset.method_percentage = (
                asset.porcentaje_anual * asset.method_period / 12)


    @api.multi
    def _porcentaje_amortizacion_default(self):
        return 99

    # porcentaje_amortizacion = fields.Char(string=u'Porcentaje de Amortización')
    porcentaje_amort = fields.Char(string=u'Porcentaje de Amortización')













