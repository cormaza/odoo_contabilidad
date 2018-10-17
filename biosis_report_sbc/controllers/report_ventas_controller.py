# coding=utf-8
from StringIO import StringIO
from datetime import datetime

import xlsxwriter
from xlsxwriter.utility import xl_range

from odoo import http
from odoo.http import request


class ReportVentasController(http.Controller):
    @http.route('/reports/report_ventas', type='http')
    def index(self,fecha_inicio, fecha_fin, **kw):
        data = request.env['report.ventas'].search([('fecha_emision', '>=', fecha_inicio),
                                                    ('fecha_emision', '<=', fecha_fin)])

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

            body = workbook.add_format({'font_size': 10})
            body.set_border()

            hoja = workbook.add_worksheet(u'Reporte de Factura de Clientes')
            # cabecera
            titulo = u'REPORTE DE FACTURAS DE CLIENTE'
            format1 = workbook.add_format(
                {'font_size': 11, 'align': 'center', 'valign': 'vcenter',
                 'bold': True, 'bg_color': '#76526C', 'color': '#fffff',
                 'font_name': 'Arial Narrow'})


            hoja.merge_range('B2:K2', titulo, format1)

            hoja.set_column('A:A', 8)
            hoja.set_column('B:B', 12)
            hoja.set_column('C:C', 16)
            hoja.set_column('D:D', 29)
            hoja.set_column('E:E', 16)
            hoja.set_column('F:F', 20)
            hoja.set_column('G:G', 16)
            hoja.set_column('H:H', 16)
            hoja.set_column('I:I', 15)
            hoja.set_column('J:J', 15)
            hoja.set_column('K:K', 18)

            hoja.write_row(2, 1,
                           (u'N° ORDEN',
                            u'OLE/OLI',
                            u'CLIENTE',
                            u'BOOKING',
                            u'COMPROBANTE',
                            u'IMP.FACTURA',
                            u'IMP.DETRACCION',
                            u'IMP.NETO',
                            u'FECHA EMISION',
                            u'FECHA VENCIMIENTO',), header)

            total_vencido = 0
            total_xvencer = 0

            row_idx = 3
            for dato in datos:
                hoja.write_row(row_idx, 1, (
                    dato.orden,
                    dato.ole_oli,
                    dato.cliente,
                    dato.booking,
                    dato.numero_documento,
                    dato.importe_factura,
                    dato.importe_detraccion,
                    dato.importe_neto,
                    dato.fecha_emision,
                    dato.fecha_vencimiento,
                ), body)
                row_idx += 1


                if dato.fecha_emision > dato.fecha_vencimiento:
                    total_vencido = total_vencido + dato.importe_neto
                else:
                    total_xvencer = total_xvencer + dato.importe_neto

                # nro ultima fila
            n = row_idx - 1
                # rango

            rango = xl_range(3, 8, n, 8)

            # mostrar titulo
            #hoja.write_row(row_idx, 7, (u'TOTAL'),header)
            #hoja.write_row(row_idx + 4, 7, u'TOTAL VENCIDO')
            #hoja.write_row(row_idx + 5, 7, u'TOTAL POR VENCER')
            # suma del rango
            #hoja.write(row_idx + 4, 8, ('=SUM(%s)' % rango))
            hoja.write(row_idx + 1, 7, (u'TOTAL'),header)
            hoja.write(row_idx + 1, 8, ('=SUM(%s)' % rango))
            hoja.write(row_idx + 2, 7, (u'TOTAL VENCIDO'),header)
            hoja.write(row_idx + 2, 8, total_vencido)
            hoja.write(row_idx + 3, 7, (u'TOTAL POR VENCER'),header)
            hoja.write(row_idx + 3, 8,  total_xvencer)
                #hoja.write(row_idx + 4, 8, total_vencido)
                #hoja.write(row_idx + 5, 8, total_xvencer)

            workbook.close()

            # Todos devuelven una instancia del objeto Respuesta.
            response = request.make_response(excel.getvalue(),
                                             headers=[('Content-Type', 'application/vnd.ms-excel'),
                                                      ('Content-Disposition',
                                                       'attachment; filename=reporte_facturas_cliente.xlsx;')])
            excel.close()

            return response

