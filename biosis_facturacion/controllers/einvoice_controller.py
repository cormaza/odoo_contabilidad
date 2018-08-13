# -*- coding: utf-8 -*-
import base64

from StringIO import StringIO
from zipfile import ZipFile

from datetime import datetime

from odoo import http
from odoo.http import serialize_exception, request, content_disposition
import requests


class EInvoiceController(http.Controller):
    @http.route('/einvoice/sunat/contingencia', type='http', auth="public")
    def index(self, fecha_inicio, fecha_fin, correlativo, motivo, **kw):
        invoices = request.env['account.invoice'].search(
            [('date_invoice', '>=', fecha_inicio), ('date_invoice', '<=', fecha_fin), ('contingencia', '=', True),
             ('enviado', '=', False)],
            order='serie_contingencia asc,correlativo_contingencia asc')
        if len(invoices) == 0:
            return request.not_fount()

        nombre_fichero = '%s-RF-%s-%s' % (
            invoices[0].company_id.partner_id.vat, datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime('%Y%m%d'),
            correlativo)
        invoice_lines = invoices.contingencia_content()
        invoice_lines = invoice_lines.replace('*MOTIVO*', motivo)

        if not invoice_lines:
            return request.not_found()
        else:
            return request.make_response(invoice_lines,
                                         [('Content-Type', 'application/octet-stream'),
                                          ('Content-Disposition', content_disposition('%s.txt' % nombre_fichero))])
