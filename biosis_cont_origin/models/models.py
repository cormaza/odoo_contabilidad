# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class biosis_cont(models.Model):
#     _name = 'biosis_cont.biosis_cont'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class SaleLinea(models.Model):
    _name = "sale.linea"
    _description = u"Linea de Automovil"

    name = fields.Char(string=u'Linea',required=True)

class SaleDeposito(models.Model):
    _name = "sale.deposito"
    _description = u"Depósito"

    name = fields.Char(string=u'Depósito', required=True)

class SaleVacio(models.Model):
    _name = "sale.vacio"
    _description = u"Vacios"

    name = fields.Char(string=u'Agente de Aduana', required=True)

class SaleTipoVacio(models.Model):
    _name = "sale.tipo.vacio"
    _description = u"Tipo Vacios"

    name = fields.Char(string=u'Tipo Vacios', required=True)

class SaleAgenteAduana(models.Model):
    _name = "sale.agente.aduana"
    _description = u"Agente de Aduana"

    name = fields.Char(string=u'Agente de Aduana', required=True)

class SaleAgentePortuario(models.Model):
    _name = "sale.agente.portuario"
    _description = u"Agente Portuario"

    name = fields.Char(string=u'Agente Portuario', required=True)