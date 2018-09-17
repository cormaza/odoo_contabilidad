# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class ResCompany(models.Model):
    _inherit = "res.company"

    #detraccion = fields.Selection([('DO', 'Una sola cuenta'), ('DM', 'Varias cuentas')])
    #diario_detraccion = fields.Many2one('account.journal', string='Diario',
     #                                   domain=[('type', '=', 'bank')])

