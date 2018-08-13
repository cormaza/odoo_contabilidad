# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

TIPO = (
    ('l', 'Liquidacion'),
    ('cc', 'Centro de Costo')
)


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    tipo = fields.Selection(TIPO, string='Tipo', default='cc')#campo nuevo