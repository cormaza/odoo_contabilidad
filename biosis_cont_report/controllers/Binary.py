# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
import base64
from zipfile import *
import StringIO

class Binary(http.Controller):
    @http.route('/biosis_cont/contabilidad/ple', type='http', website=True)
    @serialize_exception
    def consultar_ple(self, mes, year, tipo_reporte, compania,**k):
        reporte_ple = request.env['report.biosis_cont_report.report_ple']
        filename, filename_v, filecontent = reporte_ple.generate_txt_report(mes, year, tipo_reporte, compania)

        f1 = StringIO.StringIO()
        f1.write(filecontent.encode('utf-8'))

        content = f1.getvalue()
        if not filecontent:
            return request.not_found()
        else:
            if not filename:
                filename = "Nuevo.txt"

        return request.make_response(content,
                                     [('Content-Type', 'application/octet-stream'),
                                      ('Content-Disposition', content_disposition(filename + u'.txt'))])










