# coding=utf-8
from StringIO import StringIO

import xlsxwriter
from xlsxwriter.format import Format
from xlsxwriter.utility import xl_range

from odoo import http
from odoo.http import request


class ReportFacturacionController(http.Controller):
    @http.route('/reports/report_liquidacionbooking', type='http')
    def index(self, fecha_inicio, fecha_fin, **kw):
        data = request.env['report.liquidacion.booking'].search([('fecha_venc', '>=', fecha_inicio),
                                                                ('fecha_venc', '<=', fecha_fin)])

        if len(data) == 0:
            return "<h3>No existen datos para el reporte</h3>"
        else:
            return self.render_excel(data)

    def render_excel(self, datos):
        if len(datos):
            excel = StringIO()
            workbook = xlsxwriter.Workbook(excel)

            hoja = workbook.add_worksheet()

            cabecera = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_name': 'Arial Narrow',
                'bold': True,
                'font_size': 12,
                'align': 'center',
                'valign': 'vcenter'})
            frm_moneda = workbook.add_format({'num_format': 5, 'align': 'center'})

            hoja.merge_range('B2:J2', 'Reporte de Liquidaciones booking de Compras pendientes de Pago',cabecera)
            # tamaño de columna
            hoja.set_column('B:I', 20)
            #formato moneda
            hoja.set_column('I2:I1024', 15, frm_moneda)
            header = workbook.add_format()
            header.pattern = 1
            header.set_bg_color('#8f96ad')
            header.set_bold(True)
            header.set_border()

            title = workbook.add_format()
            title.set_bold()

            body = workbook.add_format()
            body.set_border()
            body.set_font_size(10)
            hoja = workbook.add_worksheet('Reporte de Liquidaciones booking de Compras pendientes de Pago')
            # datos
            hoja.write_row(2, 1,
                           (u'ORDEN',
                            u'CLIENTE',
                            u'BOOKING',
                            u'TIPO DOC',
                            u'NRO. DOCUMENTO',
                            u'IMPORTE $',
                            u'DET.',
                            u'NETO $',
                            u'FEC. EMISIÓN',
                            U'FEC. RECEPCIÓN',
                            U'FEC. VENC.'), header)
            row_idx = 3
            for dato in datos:
                hoja.write_row(row_idx, 1, (
                    dato.orden,
                    dato.cliente,
                    dato.booking,
                    dato.tipodoc,
                    dato.nrodocumento,
                    dato.importe,
                    dato.det,
                    dato.neto,
                    dato.fecemision,
                    dato.fecrecepcion,
                    dato.fecvenc
                ), body)
                row_idx += 1

                # nro ultima fila
                n = row_idx - 1
                # rango
                rango = xl_range(3, 8, n, 8)
                # mostrar titulo
                hoja.write_row(row_idx + 3, 7, u'TOTAL', header)
                # suma del rango
                hoja.write(row_idx + 4, 8, ('=SUM(%s)' % rango), frm_moneda)

            workbook.close()

            # Todos devuelven una instancia del objeto Respuesta.
            response = request.make_response(excel.getvalue(),
                                             headers=[('Content-Type', 'application/vnd.ms-excel'),
                                                      ('Content-Disposition',
                                                       'attachment; filename=reporte_liquidacion_booking.xlsx;')])
            excel.close()

            return response
