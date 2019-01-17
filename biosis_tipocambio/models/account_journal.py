# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_destino_debit_id = fields.Many2one('account.account',string=u'Cuenta Destino Débito', domain="[('code', '=like','9%')]")
    account_destino_credit_id = fields.Many2one('account.account',string=u'Cuenta Destino Crédito', domain="[('code', '=like','79%')]")
