# coding=utf-8
from StringIO import StringIO

import xlsxwriter
from xlsxwriter.utility import xl_range
from xlsxwriter.format import Format

from odoo import http
from odoo.http import request


class ReportFacturacionController(http.Controller):
    @http.route('/reports/report_liquidacioncompra', type='http')
    def index(self, fecha_inicio, fecha_fin, **kw):
        data = request.env['report.liquidacion.compra'].search([('fecha_venc', '>=', fecha_inicio),
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
            # formato moneda
            frm_moneda = workbook.add_format({'num_format': 5, 'align': 'center'})

            hoja.merge_range('B2:J2', 'Reporte de Liquidaciones y Facturas de Compras pendientes de Pago',cabecera)
            # tamaño de columna
            hoja.set_column('B:J', 16)
            # toda la columna de formato moneda
            hoja.set_column('J2:J1024', 15, frm_moneda)
            # formato cabecera
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
            hoja = workbook.add_worksheet('Reporte de Liquidaciones y Facturas de Compras pendientes de Pago')
            # datos
            hoja.write_row(2, 1,
                           (u'N DOCUMENTO',
                            u'OLE/OLI',
                            u'FECHA EMISIÓN',
                            u'FECHA RECEPCIÓN',
                            u'FECHA VENCIMIENTO',
                            u'DIAS CRÉDITO',
                            u'FECHA DE CORTE',
                            u'FECHA DE PAGO PROGRAMADA',
                            u'IMPORTE TOTAL'), header)
            row_idx = 3
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
                    dato.total

                ), body)
                row_idx += 1

                # nro ultima fila
                n = row_idx - 1
                # rango
                rango = xl_range(3, 9, n, 9)
                # mostrar titulo
                hoja.write_row(row_idx + 3, 9, u'TOTAL', header)
                # suma del rango
                hoja.write(row_idx + 3, 9, ('=SUM(%s)' % rango), frm_moneda)

            workbook.close()

            # Todos devuelven una instancia del objeto Respuesta.
            response = request.make_response(excel.getvalue(),
                                             headers=[('Content-Type', 'application/vnd.ms-excel'),
                                                      ('Content-Disposition',
                                                       'attachment; filename=reporte_liquidacion_compra.xlsx;')])
            excel.close()

            return response
