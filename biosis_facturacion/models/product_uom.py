# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductUOM(models.Model):
    _inherit = 'product.uom'

    codigo_ubl = fields.Char('Código UBL')