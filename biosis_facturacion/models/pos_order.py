# -*- coding: utf-8 -*-

from odoo import api, models, _, fields

class PorOrder(models.Model):
    _inherit = 'pos.order'

    numero_comprobante = fields.Char(related='invoice_id.numero_comprobante')
    codigo_2d = fields.Char(related='invoice_id.codigo_2d')