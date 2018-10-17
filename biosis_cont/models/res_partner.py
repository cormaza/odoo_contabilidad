# -*- coding: utf-8 -*-
import requests

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    limit_credito = fields.Float(string='Limite Credito', digits=(6, 2))
