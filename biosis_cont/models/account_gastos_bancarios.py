# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class AccountGastosBancarios(models.Model):
    _name = 'account.gastos_bancarios'
    _description = 'Gastos Bancarios'
    _order = 'secuencia'
    _rec_name = 'nombre'

    secuencia = fields.Integer(required=True, default=1)
    descripcion = fields.Char(string='Nombre corto', translate=True)
    tipo_uso = fields.Selection([('N', 'Ninguno'), ('B', 'Banco')],
                                    string='Tipo', required=True, default="N")
    nombre = fields.Char(string=u'Nombre', required=True, translate=True)
    id_cuenta = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Cuenta Ingreso',
                                 ondelete='restrict')
    destino_cuenta  = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Cuenta Destino',
                                 ondelete='restrict')
