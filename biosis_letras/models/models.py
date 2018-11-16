# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class biosis_letras(models.Model):
#     _name = 'biosis_letras.biosis_letras'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

#
# # -*- coding: utf-8 -*-
# import self as self
#
# from odoo import models, fields
#
# class letrasporcobrar(models.Model):
#     _name = 'biosis_letras.registrarletra'
#     _auto = 'descripcionconcepto'
#
#     nombre_cliente = fields.Char(String=u'Nombre Cliente', size=200)
#     ruc = fields.Char(String=u'Ruc')
#     direccion = fields.Char(String=u'Dirección', size=200)
#     importe = fields.Float(String=u'Importe')
#     descripcionconcepto = fields.Char(String=u'DescripciónConcepto')
#     fechagiro = fields.Date(String=u'Fecha Giro')
#     fechavencimiento = fields.Date(String=u'Fecha Vencimiento')
#     nrocorrelativoletra = fields.Char(String=u'Numero correlativo de letra')
#     # lanze el popup apenas exista un cambio
