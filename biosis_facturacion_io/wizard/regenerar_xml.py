# -*- coding: utf-8 -*-
import base64

from datetime import datetime
from xlrd import open_workbook, xldate_as_tuple
from zipfile import ZipFile

from odoo import models, fields, api, _


class EInvoiceRegenerarXML(models.Model):
    _name = 'einvoice.ie.regenerar_xml'

    fecha_inicio = fields.Date('Fecha de inicio')
    fecha_fin = fields.Date('Fecha de fin')

    @api.multi
    def regenerar_xml(self):
        invoice_obj = self.env['account.invoice']

        for wiz in self:
            invoices = invoice_obj.search(
                [('date_invoice', '>=', wiz.fecha_inicio), ('date_invoice', '<=', wiz.fecha_fin),
                 ('enviado', '=', False), ('state', '=', 'open')])
            invoices.regenerar_xml()
