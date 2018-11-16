# coding=utf-8
from StringIO import StringIO
from datetime import datetime

import xlsxwriter

from odoo import http
from odoo.http import request


class ReportLiquidacionCompraController(http.Controller):
    @http.route('/reports/report_factura', type='http')
    def index(self, **kw):
        gestion_lines = request.env['facturacion.report'].search([])
        # if len(gestion_lines) == 0:
        #     return "<h3>No existen datos para el reporte</h3>"
        # else:
        return self.render_excel(gestion_lines)

    def render_excel(self, datos):
        if len(datos):
            excel = StringIO()
            workbook = xlsxwriter.Workbook(excel)

            header = workbook.add_format()
            header.pattern = 1
            header.set_bg_color('#8f96ad')
            header.set_bold(True)
            header.set_border()

            title = workbook.add_format()
            title.set_bold()
            title.set_font_size(14)

            body = workbook.add_format()
            body.set_border()

            hoja = workbook.add_worksheet(u'Reporte de Facturación')
            # cabecera


            hoja.write_row(1, 1,
                           (u'N DOCUMENTO',
                            u'OLE/OLI',
                            u'FECHA EMISIÓN',
                            u'FECHA RECEPCIÓN',
                            u'FECHA VENCIMIENTO',
                            u'DIAS CRÉDITO',
                            u'FECHA DE CORTE',
                            u'FECHA DE PAGO PROGRAMADA',
                            u'IMPORTE TOTAL USD'), header)
            row_idx = 2
            for dato in datos:
                hoja.write_row(row_idx, 1, (
                    dato.num_documento,
                    dato.ole_oli,
                    dato.fecha_factura,
                    dato.fecha_recepcion,
                    dato.fecha_venc,
                    dato.plazo_pago,
                    dato.fecha_corte,
                    dato.fecha_pago,
                    dato.total,
                ), body)
                row_idx += 1

            workbook.close()

            # Todos devuelven una instancia del objeto Respuesta.
            response = request.make_response(excel.getvalue(),
                                             headers=[('Content-Type', 'application/vnd.ms-excel'),
                                                      ('Content-Disposition',
                                                       'attachment; filename=reporte_facturacion.xlsx;')])
            excel.close()

            return response
