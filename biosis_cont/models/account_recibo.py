# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountRecibos(models.Model):
    _inherit = 'account.invoice'

    is_recibo = fields.Boolean()





