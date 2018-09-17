# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class biosis_cont_liquidacion(models.Model):
#     _name = 'biosis_cont_liquidacion.biosis_cont_liquidacion'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    liquidacion_one_id = fields.Many2one('account.liquidacion', string='Liquidacion Padre')
    partner_pago = fields.Many2one('res.partner', string='Cliente relacionado', states={'draft': [('readonly', False)]})
