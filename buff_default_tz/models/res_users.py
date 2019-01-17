# -*- coding: utf-8 -*-
# © <2017> <builtforfifty>

from odoo import models, fields, api, exceptions, _

class res_users(models.Model):
    _inherit = 'res.users'

    @api.multi
    def set_default_tz(self):
        if not self.tz:
            raise exceptions.ValidationError(_('Please select a Timezone.'))
        users = self.env['res.users'].search([])
        for user in users:
            user.write({
                'tz': self.tz
            })
        self.env['ir.values'].sudo().set_default(
            'res.partner', 'default_tz', self.tz)
