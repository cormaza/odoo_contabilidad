# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductoBanana(models.Model):
    _inherit = 'product.product'

    peso_bruto = fields.Float('Peso bruto')