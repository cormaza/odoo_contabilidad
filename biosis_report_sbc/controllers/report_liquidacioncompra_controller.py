# coding=utf-8
from StringIO import StringIO
from datetime import datetime

import xlsxwriter

from odoo import http
from odoo.http import request


class ReportFacturacionController(http.Controller):
    @http.route('/reports/report_liquidacioncompra', type='http')
    def index(self,fecha_inicio, fecha_fin, **kw):
        data = request.env['report.liquidacion.compra'].search([('fecha_factura', '>=', fecha_inicio),
                                                                ('fecha_factura', '<=', fecha_fin)])

        if len(data) == 0:
            return "<h3>No existen datos para el reporte</h3>"
        else:
            return self.render_excel(data)

    def render_excel(self, datos):
        if len(datos):
            excel = StringIO()
            workbook = xlsxwriter.Workbook(excel)

            header = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_name': 'Arial Narrow',
                'bold': True,
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#efa9db'
            })

            body = workbook.add_format({'font_size': 9})
            body.set_border()

            hoja = workbook.add_worksheet(u'Reporte de Liquidaciones y Facturas de Compras pendientes de Pago')
            # cabecera
            titulo = u'REPORTE DE LIQUIDACIONES Y FACTURAS DE PROVEEDOR PENDIENTES DE PAGO'
            format1 = workbook.add_format(
                {'font_size': 11, 'align': 'center', 'valign': 'vcenter',
                 'bold': True, 'bg_color': '#76526C', 'color': '#fffff',
                 'font_name': 'Arial Narrow'})


            hoja.merge_range('B2:L2', titulo, format1)

            hoja.set_column('A:A', 8)
            hoja.set_column('B:B', 20)
            hoja.set_column('C:C', 12)
            hoja.set_column('D:D', 16)
            hoja.set_column('E:E', 16)
            hoja.set_column('F:F', 20)
            hoja.set_column('G:G', 16)
            hoja.set_column('H:H', 16)
            hoja.set_column('I:I', 26)
            hoja.set_column('J:J', 9)
            hoja.set_column('K:K', 15)
            hoja.set_column('L:L', 15)

            hoja.write_row(2, 1,
                           (u'N° DOCUMENTO',
                            u'OLE/OLI',
                            u'FECHA EMISIÓN',
                            u'FECHA RECEPCIÓN',
                            u'FECHA VENCIMIENTO',
                            u'DIAS CRÉDITO',
                            u'FECHA DE CORTE',
                            u'FECHA DE PAGO PROGRAMADA',
                            u'MONEDA',
                            u'IMPORTE TOTAL',
                            u'SALDO'), header)
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
                    dato.moneda,
                    dato.total,
                    dato.saldo,
                ), body)
                row_idx += 1

            workbook.close()

            # Todos devuelven una instancia del objeto Respuesta.
            response = request.make_response(excel.getvalue(),
                                             headers=[('Content-Type', 'application/vnd.ms-excel'),
                                                      ('Content-Disposition',
                                                       'attachment; filename=reporte_liquidacion_compra.xlsx;')])
            excel.close()

            return response

