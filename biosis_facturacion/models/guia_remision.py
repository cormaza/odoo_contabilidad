# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
import bs4, urllib2, urllib
from datetime import datetime, date


class GuiaRemisionRT(models.Model):
    _inherit = 'account.invoice'

    motivo_traslado = fields.Many2one('biosis.common.sunat.anexo5.tabla20', string='Motivo de traslado')
    destinatario = fields.Many2one('res.partner', string='Destinatario')
    proveedor = fields.Many2one('res.partner', string='Proveedor')
    tipo_transporte = fields.Selection([('publico','PUBLICO'),('privado','PRIVADO')],string='Tipo de transporte')
    direccion_llegada = fields.Many2one('res.partner', string='Dirección de llegada')
    direccion_partida = fields.Many2one('res.partner', string='Dirección de partida')
    transbordo_prog = fields.Boolean(string='Transbordo programado')
    transporte_sub_contr = fields.Boolean(string='Transporte Sub-Contratado')
    emp_transporte = fields.Many2one('res.partner', string='Empresa de transporte')
    fecha_entrega_t = fields.Date(string='Fecha de entrega al transportista')
    observaciones = fields.Text(string='Observaciones')