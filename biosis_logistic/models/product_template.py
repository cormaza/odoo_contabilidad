# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
import bs4, urllib2, urllib
from datetime import datetime, date, timedelta

TIPO_SERVICIO = (
    (u'deposito', u'Depósito'),
    (u'vacio', u'Vacío'),
    (u'agente_aduana', u'Agente aduana'),
    (u'agente_portuario', u'Agente portuario'),
    (u'agente_carga', u'Agente de carga'),
    (u'transporte', u'Transporte'),
    (u'resguardo', u'Resguardo'),
    (u'cuadrilla', u'Cuadrilla'),
    (u'aforo', u'Aforo/Inspección'),
    (u'profit', u'Profit'),
    (u'otros', u'Otros'),
)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Se agregan datos para el caso de servicios en los que se puede determinar a que tipo pertenece
    tipo_servicio = fields.Selection(TIPO_SERVICIO, u'Tipo de servicio')
    aereo = fields.Boolean(u'Aplica para vía aérea')
    maritimo = fields.Boolean(u'Aplica para vía marítima')
    fcl = fields.Boolean(u'Aplica para Full Container Load')
    lcl = fields.Boolean(u'Aplica para Less Container Load')
    linea_naviera_ids = fields.Many2many('sale.linea', string=u'Líneas navieras')
    tipo_contenedor_ids = fields.Many2many('sale.contenedor.tipo', string=u'Contenedores FCL')

    @api.constrains('tipo_contenedor_ids')
    def _check_tipo_contenedor_ids(self):
        if self.fcl:
            if not self.tipo_contenedor_ids or len(self.tipo_contenedor_ids) < 0:
                raise ValidationError(u'Debe seleccionar los contenedores que aplican para el servicio')

    @api.constrains('fcl', 'lcl')
    def _check_fcl_lcl(self):
        if self.maritimo:
            if not self.fcl and not self.lcl:
                raise ValidationError(u'Debe seleccionar si aplica para Full Container Load o Less Container Load')

    @api.onchange('tipo_servicio')
    def _onchange_tipo_servicio(self):
        res = {'value': {}}
        if self.tipo_servicio in ('agente_portuario', 'vacio'):
            res['value']['maritimo'] = True

        if self.tipo_servicio in ('agente_carga',):
            res['value']['maritimo'] = True
            res['value']['lcl'] = True
        if self.tipo_servicio in (u'profit',):
            res['value']['maritimo'] = False
            res['value']['lcl'] = False
        return res
