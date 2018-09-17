# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from odoo import models, fields, api

"""
    Tablas ANEXO 3 SUNAT
"""


class PleCubso(models.Model):
    _name = 'biosis.report.ple.cubso'
    _description = u'CATÁLOGO ÚNICO DE BIENES, SERVICIOS Y OBRAS - CUBSO'
    _rec_name = 'titulo'

    codigo = fields.Char(string=u'Código')
    titulo = fields.Char(string=u'Título')
    tipo_item = fields.Char(string=u'Tipo item')
