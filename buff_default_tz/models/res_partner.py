# -*- coding: utf-8 -*-
# © <2017> <builtforfifty>

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def get_default_tz(self):
        return self.env['ir.values'].sudo().get_default(
            'res.partner', 'default_tz') or False

    tz = fields.Selection(default=get_default_tz)
