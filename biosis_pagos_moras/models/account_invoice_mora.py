# -*- coding: utf-8 -*-
from datetime import datetime, date
from StringIO import StringIO
import bs4
import urllib2
from odoo import models, fields, api, _
import base64
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools import float_is_zero, float_compare
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_boleta_mora = fields.Boolean(string=u"Boleta Mora", required=True, default=False)
    #fichero = fields.Binary(u'Archivo CREP')





