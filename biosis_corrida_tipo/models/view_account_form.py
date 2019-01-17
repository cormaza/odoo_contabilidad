# -*- coding: utf-8 -*-

from odoo import models, fields


class account_account_form(models.Model):
    _inherit = 'account.account'

    corrida = fields.Boolean(string=u'Afecto a tipo de corrida')
