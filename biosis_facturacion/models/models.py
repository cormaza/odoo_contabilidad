# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PuertoEmbarque(models.Model):
    _name = 'biosis.facturacion.puertoembarque'
    _description = u'Puertos de Embarque'

    name = fields.Char(string=u'Nombre')


class PuertoDestino(models.Model):
    _name = 'biosis.facturacion.puertodestino'
    _description = u'Puertos de Destino'

    name = fields.Char(string=u'Nombre')


class FormaPago(models.Model):
    _name = 'biosis.facturacion.formapago'
    _description = u'Forma de pago'

    name = fields.Char(string=u'Nombre')


class MedioTransporte(models.Model):
    _name = 'biosis.facturacion.mediotransporte'
    _description = u'Medio de transporte'

    name = fields.Char(string=u'Nombre')


class CondicionVenta(models.Model):
    _name = 'biosis.facturacion.condicionventa'
    _description = u'Condicion de Venta'

    name = fields.Char(string=u'Nombre')


class Consignatario(models.Model):
    _name = 'biosis.facturacion.consignatario'
    _description = u'Consignatario'

    name = fields.Char(string=u'Nombre')

    @api.model
    def create(self, vals):
        vals['name'] = ' '.join(vals['name'].strip().split('\n'))
        return super(Consignatario, self).create(vals)
