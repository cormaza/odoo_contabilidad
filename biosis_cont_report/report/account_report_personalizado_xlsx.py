# -*- coding: utf-8 -*-
import datetime
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class BiosisContReportPersonalizadoXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, lines):
        reporte_balance = self.env['report.biosis_cont_report.balance_comprobacion']
        report_lines = reporte_balance.get_account_lines(data)
        report_name = u"Reporte Personalizado por Diarios"
        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])

        # Formato para celdas
        format1 = workbook.add_format(
            {'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format({'font_size': 11, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_sumas = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_saldos = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_inv = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#e4fff6'})
        format_nat = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f9f7f7'})
        format_fun = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f8d9d9'})
        format_footer = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#ccff33'})
        # Especificamos ancho de columnas
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 50)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        # Definimos la cabecera del reporte
        sheet.merge_range('A1:L1', report_name, format1)
        sheet.merge_range('A2:A3', u'CUENTA', format2)
        sheet.merge_range('B2:B3', u'DESCRIPCIÓN', format2)
        sheet.merge_range('C2:D2', u'SUMAS DEL MAYOR', format2)
        sheet.write('C3', u'DEBE', format2)
        sheet.write('D3', u'HABER', format2)
        sheet.merge_range('E2:F2', u'SALDOS', format2)
        sheet.write('E3', u'DEUDOR', format2)
        sheet.write('F3', u'ACREEDOR', format2)
        sheet.merge_range('G2:H2', u'INVENTARIO', format2)
        sheet.write('G3', u'ACTIVO', format2)
        sheet.write('H3', u'PASIVO', format2)
        sheet.merge_range('I2:J2', u'RESULTADO POR NATURALEZA', format2)
        sheet.write('I3', u'PERDIDA', format2)
        sheet.write('J3', u'GANANCIA', format2)
        sheet.merge_range('K2:L2', u'RESULTADO POR FUNCIÓN', format2)
        sheet.write('K3', u'PERDIDA', format2)
        sheet.write('L3', u'GANANCIA', format2)

        # Loop de report_lines
        i = 2
        total_debe = total_haber = total_deudor = total_acreedor = total_activo = total_pasivo = total_perdida = total_ganancia = total_perdida1 = total_ganancia1 = 0
        for line in report_lines:
            if line['level'] != 0:
                sheet.write(i, 0, line['codigo'], format3)
                sheet.write(i, 1, line['name'], format3)
                sheet.write(i, 2, line['debit'], format_sumas)
                sheet.write(i, 3, line['credit'], format_sumas)
                # sheet.write(i, 4, (line['debit']-line['credit']) if ((line['debit']-line['credit'])>0) else 0, format3)
                # sheet.write(i, 5, (line['credit']-line['debit']) if ((line['credit']-line['debit'])>0) else 0, format3)
                sheet.write(i, 4, line['deudor'], format_saldos)
                sheet.write(i, 5, line['acreedor'], format_saldos)
                sheet.write(i, 6, line['activo'], format_inv)
                sheet.write(i, 7, line['pasivo'], format_inv)
                sheet.write(i, 8, line['perdida'], format_nat)
                sheet.write(i, 9, line['ganancia'], format_nat)
                sheet.write(i, 10, line['perdida1'], format_fun)
                sheet.write(i, 11, line['ganancia1'], format_fun)
                total_debe += line['debit']
                total_haber += line['credit']
                total_deudor += line['deudor']
                total_acreedor += line['acreedor']
                total_activo += line['activo']
                total_pasivo += line['pasivo']
                total_perdida += line['perdida']
                total_ganancia += line['ganancia']
                total_perdida1 += line['perdida1']
                total_ganancia1 += line['ganancia1']
            i += 1
        print total_debe
        total_i = i + 1
        resultados_i = i + 2
        sumas_i = i + 3

        # Filas de sumas
        # Totales
        sheet.merge_range('A' + str(total_i) + ':B' + str(total_i), u'TOTALES', format2)
        sheet.write('C' + str(total_i), total_debe, format_footer)
        sheet.write('D' + str(total_i), total_haber, format_footer)
        sheet.write('E' + str(total_i), total_deudor, format_footer)
        sheet.write('F' + str(total_i), total_acreedor, format_footer)
        sheet.write('G' + str(total_i), total_activo, format_footer)
        sheet.write('H' + str(total_i), total_pasivo, format_footer)
        sheet.write('I' + str(total_i), total_perdida, format_footer)
        sheet.write('J' + str(total_i), total_ganancia, format_footer)
        sheet.write('K' + str(total_i), total_perdida1, format_footer)
        sheet.write('L' + str(total_i), total_ganancia1, format_footer)

        # Resultados de ejercicio
        sheet.merge_range('A' + str(resultados_i) + ':B' + str(resultados_i), u'RESULTADO EJERCICIO', format2)
        sheet.write('B' + str(resultados_i), '', format_footer)
        sheet.write('C' + str(resultados_i), '', format_footer)
        sheet.write('D' + str(resultados_i), '', format_footer)
        sheet.write('E' + str(resultados_i), '', format_footer)
        sheet.write('F' + str(resultados_i), '', format_footer)
        # INVENTARIO
        if total_activo > total_pasivo:
            diferencia = total_activo - total_pasivo
            print diferencia
            sheet.write('G' + str(resultados_i), '', format_footer)
            sheet.write('H' + str(resultados_i), diferencia, format_footer)
        else:
            diferencia = total_pasivo - total_activo
            print diferencia
            sheet.write('G' + str(resultados_i), diferencia, format_footer)
            sheet.write('H' + str(resultados_i), '', format_footer)
            # RESULTADO POR NATURALEZA
        if total_perdida > total_ganancia:
            diferencia = total_perdida - total_ganancia
            print diferencia
            sheet.write('I' + str(resultados_i), '', format_footer)
            sheet.write('J' + str(resultados_i), diferencia, format_footer)
        else:
            diferencia = total_ganancia - total_perdida
            print diferencia
            sheet.write('I' + str(resultados_i), diferencia, format_footer)
            sheet.write('J' + str(resultados_i), '', format_footer)
            # RESULTADO POR NATURALEZA
        if total_perdida1 > total_ganancia1:
            diferencia = total_perdida1 - total_ganancia1
            print diferencia
            sheet.write('K' + str(resultados_i), '', format_footer)
            sheet.write('L' + str(resultados_i), diferencia, format_footer)
        else:
            diferencia = total_ganancia1 - total_perdida1
            print diferencia
            sheet.write('K' + str(resultados_i), diferencia, format_footer)
            sheet.write('L' + str(resultados_i), '', format_footer)
        # Sumas de igualdad
        sheet.merge_range('A' + str(sumas_i) + ':B' + str(sumas_i), u'SUMAS IGUALDAD', format2)
        sheet.write_formula('C' + str(sumas_i), '{=SUM(' + 'C' + str(sumas_i - 2) + ':' + 'C' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('D' + str(sumas_i), '{=SUM(' + 'D' + str(sumas_i - 2) + ':' + 'D' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('E' + str(sumas_i), '{=SUM(' + 'E' + str(sumas_i - 2) + ':' + 'E' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('F' + str(sumas_i), '{=SUM(' + 'F' + str(sumas_i - 2) + ':' + 'F' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('G' + str(sumas_i), '{=SUM(' + 'G' + str(sumas_i - 2) + ':' + 'G' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('H' + str(sumas_i), '{=SUM(' + 'H' + str(sumas_i - 2) + ':' + 'H' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('I' + str(sumas_i), '{=SUM(' + 'I' + str(sumas_i - 2) + ':' + 'I' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('J' + str(sumas_i), '{=SUM(' + 'J' + str(sumas_i - 2) + ':' + 'J' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('K' + str(sumas_i), '{=SUM(' + 'K' + str(sumas_i - 2) + ':' + 'K' + str(sumas_i - 1) + ')}',
                            format_footer)
        sheet.write_formula('L' + str(sumas_i), '{=SUM(' + 'L' + str(sumas_i - 2) + ':' + 'L' + str(sumas_i - 1) + ')}',
                            format_footer)

BiosisContReportPersonalizadoXlsx('report.biosis_cont_report.report_personalizado_xls.xlsx','account.personalizado')