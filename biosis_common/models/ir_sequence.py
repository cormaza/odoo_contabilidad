# coding=utf-8
from odoo import models, fields, api
from datetime import date


class IrSequenceReseteo(models.Model):
    _inherit = 'ir.sequence'

    ultimo_ciclo = fields.Integer()
    ciclo = fields.Selection(((u'anio', u'Año'), (u'mes', u'Mes'), (u'dia', u'Día'), (u'ninguno', u'Ninguno')),
                             u'Ciclo de reseteo', default=u'ninguno')

    def _next(self):
        opciones = {
            u'anio': date.today().year,
            u'mes': date.today().month,
            u'dia': date.today().day,
            u'ninguno': -1
        }
        actual = opciones[self.ciclo]
        if actual != -1 and actual != self.ultimo_ciclo:
            self.ultimo_ciclo = actual
            self.number_next_actual = 1
        result = super(IrSequenceReseteo, self)._next()
        return result
