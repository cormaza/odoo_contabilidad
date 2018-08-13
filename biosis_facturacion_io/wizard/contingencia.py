# -*- coding: utf-8 -*-
import base64
from zipfile import ZipFile

from odoo import models, fields, api, _

MOTIVO = (
    ('1', u'Conexión a internet'),
    ('2', u'Fallas fluido eléctrico'),
    ('3', u'Desastres naturales'),
    ('4', u'Robo'),
    ('5', u'Fallas en el sistema de facturación'),
    ('6', u'Ventas'),
    ('7', u'Otros'),
)


class EInvoiceContingencia(models.TransientModel):
    _name = 'einvoice.ie.contingencia'

    fecha_inicio = fields.Date(string='Fecha de inicio')
    fecha_fin = fields.Date(string='Fecha de fin')
    correlativo = fields.Char('Correlativo', size=2)
    motivo = fields.Selection(MOTIVO, string='Motivo de contingencia')

    @api.multi
    def generar_fichero(self):
        for contingencia in self:
            return {
                'type': 'ir.actions.act_url',
                'url': '/einvoice/sunat/contingencia?fecha_inicio=%s&fecha_fin=%s&correlativo=%s&motivo=%s' % (
                    contingencia.fecha_inicio, contingencia.fecha_inicio, contingencia.correlativo, contingencia.motivo),
                'target': 'new',
            }
