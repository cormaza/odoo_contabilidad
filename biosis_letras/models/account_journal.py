# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_cobranza_dudosa_debit = fields.Many2one('account.account',string=u'Cuenta cobranza dudosa Débito', domain="[('code', '=like','684%')]")
    account_cobranza_dudosa_credit = fields.Many2one('account.account',string=u'Cuenta cobranza dudosa Crédito', domain="[('code', '=like','191%')]")
