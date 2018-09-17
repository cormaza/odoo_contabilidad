# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from odoo import models, fields, api

"""
    Tablas Bienes/Servicios sujetos a detracción
"""
class bsdetraccion(models.Model):
    _name = 'bienes.servicios.detraccion'
    _description = u'TABLA ANEXO IV: Catálogo número 54.'
    _order = 'codigo'
    _rec_name = 'descripcion'

    codigo = fields.Char(string=u'Código',required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)
    monto_minimo = fields.Float(string=u'Monto mínimo s/.')
    porcentaje = fields.Float(string='Porcentaje',digits=(6,3))
    comentario = fields.Text(string='Comentario')
    vigente = fields.Boolean(string='Vigente',default=False)



