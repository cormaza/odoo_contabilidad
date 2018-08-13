# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import bs4, urllib2, urllib
from datetime import datetime, date

class CentroCostos(models.Model):
    _name="account.centro.costos"
    _description = "Centro Costos"

    nombre = fields.Char(string=u'Nombre de Centro de Costos', required=True)
    diario = fields.Many2one('account.journal', string=u'Diario de Costos', domain=[('code', '=', 'CC')])
    cuentas_control_ids = fields.Many2many('account.account', 'account_account_type_rel', 'journal_id', 'account_id', string=u'Cuentas de control')

    account_92_id = fields.Many2one('account.account', string=u'Cuenta destino 92')
    account_94_id = fields.Many2one('account.account', string=u'Cuenta destino 94')
    account_95_id = fields.Many2one('account.account', string=u'Cuenta destino 95')
    account_97_id = fields.Many2one('account.account', string=u'Cuenta destino 97')
    porcentaje_92 = fields.Float(string=u'Porcentaje correspondiente 92')
    porcentaje_94 = fields.Float(string=u'Porcentaje correspondiente 94')
    porcentaje_95 = fields.Float(string=u'Porcentaje correspondiente 95')
    porcentaje_97 = fields.Float(string=u'Porcentaje correspondiente 97')

    @api.model
    def create(self, vals):
        cc = super(CentroCostos, self).create(vals)
        return cc

