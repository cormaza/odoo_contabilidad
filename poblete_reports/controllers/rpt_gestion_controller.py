# coding=utf-8
from StringIO import StringIO

from datetime import datetime

import xlsxwriter

from odoo import http
from odoo.http import request


class ReportGestionController(http.Controller):
    @http.route('/reports/gestion', type='http', auth="user")
    def index(self, mes, **kw):
        gestion_lines = request.env['suscription.gestion.report'].search([('inv_mes', '=', mes)],
                                                                         order='partner_id asc')
        if len(gestion_lines) == 0:
            return "<h3>No existen datos para el reporte</h3>"
        else:
            return self.render_excel(gestion_lines,mes)

    def render_excel(self, datos,mes):
        if len(datos):
            excel = StringIO()
            workbook = xlsxwriter.Workbook(excel)

            header = workbook.add_format()
            header.pattern = 1
            header.set_bg_color('#C1C0BB')
            header.set_bold(True)
            header.set_border()

            title = workbook.add_format()
            title.set_bold()
            title.set_font_size(14)

            body = workbook.add_format()
            body.set_border()

            hoja = workbook.add_worksheet(u'Reporte de gestión')

            hoja.write_row(1, 1,
                           (u'STAND / # REFERENCIA DE SUSCRIPCIÓN',
                            u'NOMBRE',
                            u'DNI / RUC',
                            u'IMPORTE ALQUILER SIN IGV',
                            u'IGV',
                            u'MORAS EN SOLES',
                            u'MORAS EN DÍAS',
                            u'ESTADO DE PAGO',
                            u'GIRO DE NEGOCIO'), header)

            row_idx = 2
            for dato in datos:
                hoja.write_row(row_idx, 1, (
                    dato.subscription_id.code,
                    dato.partner_id.name,
                    dato.partner_id.vat or '',
                    dato.total_sin_igv,
                    dato.total_igv,
                    dato.total_mora,
                    dato.dias_mora,
                    dato.inv_state == 'open' and 'Facturado' or 'Pagado',
                    dato.partner_id.giro_negocio or '',
                ), body)
                row_idx += 1

            workbook.close()

            response = request.make_response(excel.getvalue(),
                                             headers=[('Content-Type', 'application/vnd.ms-excel'),
                                                      ('Content-Disposition',
                                                       'attachment; filename=RPT_GESTION_MES_%s.xlsx;' % mes)])
            excel.close()

            return response
