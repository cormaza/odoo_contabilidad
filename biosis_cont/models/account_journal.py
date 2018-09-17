# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    itf_account_id = fields.Many2one('account.account',string=u'Cuenta de ITF por defecto',
                                     default=lambda self: self.env['account.account'].search([('code','=like','641200%')],limit=1))
    type = fields.Selection(selection_add=[('apertura','Apertura'),('cierre','Cierre')])
