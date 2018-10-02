# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from odoo import models, fields, api

"""
    CUBSO
"""
class PleCubso(models.Model):
    _name = 'ple.cubso'
    _description = u'CATÁLOGO ÚNICO DE BIENES, SERVICIOS Y OBRAS - CUBSO'
    _rec_name = 'titulo'

    codigo = fields.Char(string=u'Código')
    titulo = fields.Text(string=u'Título')
    tipo_item = fields.Char(string=u'Tipo item')

class PleAnexo3Tabla14(models.Model):
    _name = 'ple.anexo3.tabla14'
    _description = u'TABLA 14: MÉTODO DE VALUACIÓN'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    codigo_cubso = fields.Many2one('ple.cubso', string=u'CUBSO')
    codigo_valuacion = fields.Many2one('ple.anexo3.tabla14', string=u'Valuación')






