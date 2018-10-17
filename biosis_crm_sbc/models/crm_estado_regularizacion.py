# coding=utf-8
from odoo import models, fields, api

TIPO_OPERACION=(
    ('i', u'Importación'),
('e',u'Exportación')
)

class CrmEstadoRegularizacion(models.Model):
    _name='crm.estado_regularizacion'
    name=fields.Char(string=u'Estado')
    tipo_operacion= fields.Selection(TIPO_OPERACION)
