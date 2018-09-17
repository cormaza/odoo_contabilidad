# -*- coding: utf-8 -*-
import datetime
import calendar
import re

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

MES_SPA = {
    '1': u'ENERO',
    '2': u'FEBRERO',
    '3': u'MARZO',
    '4': u'ABRIL',
    '5': u'MAYO',
    '6': u'JUNIO',
    '7': u'JULIO',
    '8': u'AGOSTO',
    '9': u'SETIEMBRE',
    '10': u'OCTUBRE',
    '11': u'NOVIEMBRE',
    '12': u'DICIEMBRE'
}

class AccountReportLogic(models.AbstractModel):
    _name = "account.report.logic"
    _description = "Contiene la logica de los reportes para Sunat"

    def get_report_body(self,workbook,data):
        return {
            '010100':u'010100',
            '010200':u'010200',
            '030100':self.get_report_030100,
            '030200':u'030200',
            '030300':u'030300',
            '030400':u'030400',
            '030500':u'030500',
            '030600':u'030600',
            '030700':u'030700',
            '030800':u'030800',
            '030900':u'030900',
            '031100':u'031100',
            '031200':u'031200',
            '031300':u'031300',
            '031400':u'031400',
            '031500':u'031500',
            '031601':u'031601',
            '031602':u'031602',
            '031700': self.get_report_031700,
            '031800':u'031800',
            '031900':u'031900',
            '032000': self.get_report_032000,
            '032300':u'032300',
            '032400':u'032400',
            '032500':u'032500',
            '040100':u'040100',
            '050100': self.get_report_050100,
            '050300':u'050300',
            '050200':u'050200',
            '050400':u'050400',
            '060100': self.get_report_060100,
            '070100':u'070100',
            '070300':u'070300',
            '070400':u'070400',
            '080100': self.get_report_080100,
            '080200':u'080200',
            '080300':u'080300',
            '090100':u'090100',
            '090200':u'090200',
            '100100':u'100100',
            '100200':u'100200',
            '100300':u'100300',
            '100400':u'100400',
            '120100':u'120100',
            '130100':u'130100',
            '140100': self.get_report_140100,
            '140200':u'140200'
        }.get(data['tipo_reporte'])(workbook,data)

    def get_report_030100(self,workbook,data):
        reporte_balance = self.env['report.biosis_cont_report.balance_comprobacion']  # Reporte financiero(odoo)
        libro_electronico = self.env['biosis_cont_report.libro.electronico'].search(
            [('id', '=', data['libro_electronico'][0])], limit=1)
        report_lines = reporte_balance.get_account_lines(data)
        report_name = libro_electronico.nro_orden

        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])
        self.get_report_header(libro_electronico, workbook, sheet, data)
        # Definimos formatos para celdas
        format1 = workbook.add_format(
            {'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True,
             'bg_color': '#D3D3D3'})
        format2 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'text_wrap': True})
        format3 = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bold': True, 'text_wrap': True})
        format4 = workbook.add_format(
            {'font_size': 10, 'align': 'justify', 'border': 1, 'text_wrap': True})
        format_sumas = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_saldos = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_inv = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#e4fff6'})
        format_nat = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f9f7f7'})
        format_fun = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f8d9d9'})
        format_footer = workbook.add_format(
            {'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#ccff33'})

        total_ac = 0
        total_anc = 0
        total_pc = 0
        total_pnc = 0
        total_patr = 0
        # Especificamos ancho de columnas
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 5)
        sheet.set_column('D:D', 40)
        sheet.set_column('E:E', 15)

        sheet.merge_range('A8:A9', u'2018', format2)
        sheet.merge_range('B8:B9', u'EJERCICIO O\n PERIODO', format2)
        sheet.merge_range('D8:D9', u'2018', format2)
        sheet.merge_range('E8:E9', u'EJERCICIO O\n PERIODO', format2)

        sheet.write('A11', u'ACTIVO', format3)
        sheet.write('B11', u'', format3)
        sheet.write('D11', u'PASIVO Y PATRIMONIO', format3)
        sheet.write('E11', u'', format3)

        sheet.write('A12', u'', format3)
        sheet.write('B12', u'', format3)
        sheet.write('D12', u'', format3)
        sheet.write('E12', u'', format3)

        sheet.write('A13', u'ACTIVO CORRIENTE', format3)
        sheet.write('B13', u'', format3)
        sheet.write('D13', u'PASIVO CORRIENTE', format3)
        sheet.write('E13', u'', format3)

        sheet.write('A14', u'Caja y Bancos', format4)
        total_ac+=self.get_sum_accounts(report_lines,"ac","10")
        sheet.write('B14', self.get_sum_accounts(report_lines,"ac","10"), format4)
        sheet.write('D14', u'Sobregiros y Pagarés Bancarios', format4)
        total_pc+=self.get_sum_accounts(report_lines,"pc","10")
        sheet.write('E14', self.get_sum_accounts(report_lines,"pc","10"), format4)

        sheet.write('A15', u'Valores Negociables', format4)
        total_ac+=self.get_sum_accounts(report_lines,"ac","11")
        sheet.write('B15', self.get_sum_accounts(report_lines,"ac","11"), format4)
        sheet.write('D15', u'Cuentas por Pagar Comerciales', format4)
        total_pc += self.get_sum_accounts(report_lines, "pc", "42")
        sheet.write('E15', self.get_sum_accounts(report_lines,"pc","42"), format4)

        sheet.write('A16', u'Cuentas por Cobrar Comerciales', format4)
        total_ac+=self.get_sum_accounts(report_lines,"ac","12")
        sheet.write('B16', self.get_sum_accounts(report_lines,"ac","12"), format4)
        sheet.write('D16', u'Cuentas por Pagar a Vinculadas', format4)
        total_pc+=self.get_sum_accounts(report_lines,"pc","43")
        sheet.write('E16', self.get_sum_accounts(report_lines,"pc","43"), format4)

        sheet.write('A17', u'Cuentas por Cobrar a Vinculadas', format4)
        total_ac+=self.get_sum_accounts(report_lines,"ac","13")
        sheet.write('B17', self.get_sum_accounts(report_lines,"ac","13"), format4)
        sheet.write('D17', u'Otras Cuentas por Pagar', format4)
        total_pc+=self.get_sum_accounts(report_lines,"pc","40|41|47|48")
        sheet.write('E17', self.get_sum_accounts(report_lines,"pc","40|41|47|48"), format4)

        sheet.write('A18', u'Otras Cuentas por Cobrar', format4)
        total_ac+=self.get_sum_accounts(report_lines,"ac","14|16|17","19")
        sheet.write('B18', self.get_sum_accounts(report_lines,"ac","14|16|17","19"), format4)
        sheet.write('D18', u'Parte Corriente de las Deudas a Largo Plazo', format4)
        total_pc+=self.get_sum_accounts(report_lines,"pc","44|45|46")
        sheet.write('E18', self.get_sum_accounts(report_lines,"pc","44|45|46"), format4)

        sheet.write('A19', u'Existencias', format4)
        total_ac+=self.get_sum_accounts(report_lines,"ac","20|21|22|23|24|25|26|27|28","29")
        sheet.write('B19', self.get_sum_accounts(report_lines,"ac","20|21|22|23|24|25|26|27|28","29"), format4)
        sheet.write('D19', u'TOTAL PASIVO CORRIENTE', format2)
        sheet.write('E19', total_pc, format4)

        sheet.write('A20', u'Gastos Pagados por Anticipado', format4)
        total_ac+=self.get_sum_accounts(report_lines,"ac","18")
        sheet.write('B20', self.get_sum_accounts(report_lines,"ac","18"), format4)
        sheet.write('D20', u'', format2)
        sheet.write('E20', u'', format4)

        sheet.write('A21', u'TOTAL ACTIVO CORRIENTE', format2)
        sheet.write('B21', total_ac, format4)
        sheet.write('D21', u'PASIVO NO CORRIENTE', format3)
        sheet.write('E21', u'', format4)
        ###
        sheet.write('A22', u'', format2)
        sheet.write('B22', u'', format4)
        sheet.write('D22', u'Deudas a Largo Plazo', format4)
        sheet.write('E22', u'', format4)

        sheet.write('A23', u'ACTIVO NO CORRIENTE', format3)
        sheet.write('B23', u'', format4)
        sheet.write('D23', u'Cuentas por Pagar a Vinculadas', format4)
        sheet.write('E23', u'', format4)

        sheet.write('A24', u'Cuentas por Cobrar a Largo Plazo', format4)
        sheet.write('B24', u'', format4)
        sheet.write('D24', u'Ingresos Diferidos', format4)
        total_pnc+=self.get_sum_accounts(report_lines,"pnc","496")
        sheet.write('E24', self.get_sum_accounts(report_lines,"pnc","496"), format4)

        sheet.write('A25', u'Cuentas por Cobrar a Vinculadas a Largo Plazo', format4)
        sheet.write('B25', u'', format4)
        total_pnc+=self.get_sum_accounts(report_lines,"pnc","49","496")
        sheet.write('D25', u'Impuesto a la Renta y Participaciones Diferidos Pasivo', format4)
        sheet.write('E25', self.get_sum_accounts(report_lines,"pnc","49","496"), format4)

        sheet.write('A26', u'Otras Cuentas por Cobrar a Largo Plazo', format4)
        sheet.write('B26', u'', format4)
        sheet.write('D26', u' TOTAL PASIVO NO CORRIENTE', format2)
        sheet.write('E26', total_pnc, format4)

        sheet.write('A27', u'Inversiones Permanentes', format4)
        sheet.write('B27', self.get_sum_accounts(report_lines,"anc","30|31"), format4)
        sheet.write('D27', u'', format2)
        sheet.write('E27', u'', format4)

        sheet.write('A28', u'Inmuebles, Maquinaria y Equipo (neto de depreciación acumulada)', format4)
        total_anc+=self.get_sum_accounts(report_lines,"anc","32|33","39")
        sheet.write('B28', self.get_sum_accounts(report_lines,"anc","32|33","39"), format4)
        sheet.write('D28', u'TOTAL PASIVO', format2)
        sheet.write('E28', total_pc+total_pnc, format4)

        sheet.write('A29', u'Activos Intangibles (neto de amortización acumulada)', format4)
        total_anc+=self.get_sum_accounts(report_lines,"anc","34","392")
        sheet.write('B29', self.get_sum_accounts(report_lines,"anc","34","392"), format4)
        sheet.write('D29', u'', format2)
        sheet.write('E29', u'', format4)

        sheet.write('A30', u'Impuesto a la Renta y Participaciones Diferidos Activo', format4)
        total_anc+=self.get_sum_accounts(report_lines,"anc","37|40")
        sheet.write('B30', self.get_sum_accounts(report_lines,"anc","37|40"), format4)
        sheet.write('D30', u'Contingencias', format4)
        sheet.write('E30', u'', format4)

        sheet.write('A31', u'Otros Activos', format4)
        total_anc+=self.get_sum_accounts(report_lines,"anc","38")
        sheet.write('B31', self.get_sum_accounts(report_lines,"anc","38"), format4)
        sheet.write('D31', u'Interés minoritario', format4)
        sheet.write('E31', u'', format4)

        sheet.write('A32', u'TOTAL ACTIVO NO CORRIENTE', format2)
        sheet.write('B32', total_anc, format4)
        sheet.write('D32', u'', format4)
        sheet.write('E32', u'', format4)

        sheet.write('A33', u'', format2)
        sheet.write('B33', u'', format4)
        sheet.write('D33', u'PATRIMONIO NETO', format3)
        sheet.write('E33', u'', format4)

        sheet.write('A34', u'', format2)
        sheet.write('B34', u'', format4)
        sheet.write('D34', u'Capital', format4)
        total_patr += self.get_sum_accounts(report_lines, "ptn", "50")
        sheet.write('E34', self.get_sum_accounts(report_lines, "ptn", "50"), format4)

        sheet.write('A35', u'', format2)
        sheet.write('B35', u'', format4)
        sheet.write('D35', u'Capital Adicional', format4)
        total_patr+=self.get_sum_accounts(report_lines,"ptn","52")
        sheet.write('E35', self.get_sum_accounts(report_lines,"ptn","52"), format4)

        sheet.write('A36', u'', format2)
        sheet.write('B36', u'', format4)
        sheet.write('D36', u'Acciones de Inversión', format4)
        total_patr+=self.get_sum_accounts(report_lines, "ptn", "51")
        sheet.write('E36', self.get_sum_accounts(report_lines,"pn","51"), format4)

        sheet.write('A37', u'', format2)
        sheet.write('B37', u'', format4)
        sheet.write('D37', u'Excedentes de Revaluación', format4)
        total_patr += self.get_sum_accounts(report_lines, "ptn", "57")
        sheet.write('E37', self.get_sum_accounts(report_lines, "ptn", "57"), format4)

        sheet.write('A38', u'', format2)
        sheet.write('B38', u'', format4)
        sheet.write('D38', u'Reservas Legales', format4)
        total_patr += self.get_sum_accounts(report_lines, "ptn", "58")
        sheet.write('E38', self.get_sum_accounts(report_lines, "ptn", "58"), format4)

        sheet.write('A39', u'', format2)
        sheet.write('B39', u'', format4)
        sheet.write('D39', u'Otras Reservas', format4)
        total_patr += self.get_sum_accounts(report_lines, "ptn", "56")
        sheet.write('E39', self.get_sum_accounts(report_lines, "ptn", "56"), format4)

        sheet.write('A40', u'', format2)
        sheet.write('B40', u'', format4)
        sheet.write('D40', u'Resultados Acumulados', format4)
        total_patr += self.get_sum_accounts(report_lines, "ptn", "59")
        sheet.write('E40', self.get_sum_accounts(report_lines, "ptn", "59"), format4)

        sheet.write('A41', u'', format4)
        sheet.write('B41', u'', format4)
        sheet.write('D41', u'TOTAL PATRIMONIO NETO', format2)
        sheet.write('E41', total_patr, format4)

        sheet.write('A42', u'', format2)
        sheet.write('B42', u'', format4)
        sheet.write('D42', u'', format2)
        sheet.write('E42', u'', format4)

        sheet.write('A43', u'TOTAL ACTIVO', format2)
        sheet.write('B43', total_ac+total_anc, format4)
        sheet.write('D43', u'TOTAL PASIVO Y PATRIMONIO NETO', format2)
        sheet.write('E43', total_pc+total_pnc+total_patr, format4)


    def get_report_031700(self,workbook,data):
        reporte_balance = self.env['report.biosis_cont_report.balance_comprobacion'] #Reporte financiero(odoo)
        libro_electronico = self.env['biosis_cont_report.libro.electronico'].search([('id', '=', data['libro_electronico'][0])], limit=1)
        report_lines = reporte_balance.get_account_lines(data)
        report_name = libro_electronico.nro_orden

        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])
        self.get_report_header(libro_electronico,workbook,sheet,data)
        # Formato para celdas
        format1 = workbook.add_format({'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format({'font_size': 11, 'align': 'center', 'border': 1, 'bold': True, 'bg_color': '#D3D3D3'})
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
        #sheet.merge_range('A7:L7', u'BALANCE DE COMPROBACION', format1)
        sheet.merge_range('A8:A9', u'CUENTA', format2)
        sheet.merge_range('B8:B9', u'DESCRIPCIÓN', format2)
        sheet.merge_range('C8:D8', u'SUMAS DEL MAYOR', format2)
        sheet.write('C9', u'DEBE', format2)
        sheet.write('D9', u'HABER', format2)
        sheet.merge_range('E8:F8', u'SALDOS', format2)
        sheet.write('E9', u'DEUDOR', format2)
        sheet.write('F9', u'ACREEDOR', format2)
        sheet.merge_range('G8:H8', u'INVENTARIO', format2)
        sheet.write('G9', u'ACTIVO', format2)
        sheet.write('H9', u'PASIVO', format2)
        sheet.merge_range('I8:J8', u'RESULTADO POR NATURALEZA', format2)
        sheet.write('I9', u'PERDIDA', format2)
        sheet.write('J9', u'GANANCIA', format2)
        sheet.merge_range('K8:L8', u'RESULTADO POR FUNCIÓN', format2)
        sheet.write('K9', u'PERDIDA', format2)
        sheet.write('L9', u'GANANCIA', format2)

        # Loop de report_lines
        i = 8
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

    def get_report_032000(self, workbook, data):
        return True

    def get_report_080100(self,workbook,data):
        reporte_ple = self.env['report.biosis_cont_report.report_ple']
        libro_electronico = self.env['biosis_cont_report.libro.electronico'].search(
            [('id', '=', data['libro_electronico'][0])], limit=1)
        filename, filename_v, filecontent = reporte_ple.generate_txt_report(data['mes'], data['year'], data['tipo_reporte'], data['used_context']['company'])
        report_name = libro_electronico.nro_orden

        date1 = str(data['year']) + '-' + str(data['mes']) + '-' + '01'
        fecha_inicio = datetime.datetime.strptime(date1, "%Y-%m-%d").date()
        date2 = "%s-%s-%s" % (fecha_inicio.year, fecha_inicio.month, calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1])
        fecha_fin = datetime.datetime.strptime(date2, "%Y-%m-%d").date()

        report_lines = self.env['account.invoice'].search([
            ('date_invoice', '>=', fecha_inicio),
            ('date_invoice', '<=', fecha_fin),
            ('type', '=', 'in_invoice'),
            ('state', '!=', 'draft'),
            ('tipo_comprobante_id.code', 'in', ['01', '03', '07', '08']),
            ('company_id', '=', data['used_context']['company']),
            ('ple_generado', '=', True)
        ]).sorted(key=lambda r: r.date_invoice)

        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])
        self.get_report_header(libro_electronico, workbook, sheet, data)
        format1 = workbook.add_format(
            {'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'text_wrap': True,
             'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_sumas = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_saldos = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_inv = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#e4fff6'})
        format_nat = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f9f7f7'})
        format_fun = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f8d9d9'})
        format_footer = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#ccff33'})

        # Especificamos ancho de columnas
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 15)
        sheet.set_column('R:R', 15)
        sheet.set_column('S:S', 15)
        sheet.set_column('T:T', 15)
        sheet.set_column('U:U', 15)
        sheet.set_column('V:V', 15)
        sheet.set_column('W:W', 15)
        sheet.set_column('X:X', 15)
        sheet.set_column('Y:Y', 15)
        sheet.set_column('Z:Z', 15)
        sheet.set_column('AA:AA', 15)
        sheet.set_column('AB:AB', 15)

        # Definimos alto filas
        sheet.set_row(7,75)
        sheet.set_row(9,136)
        # Definimos la cabecera del reporte
        sheet.merge_range('A8:A10', u'NUMERO CORRELATIVO DEL REGISTRO O CODIGO UNICO DE LA OPERACION', format2)
        sheet.merge_range('B8:B10', u'FECHA DE EMISION DEL COMPROBANTE DE PAGO O DOCUMENTO', format2)
        sheet.merge_range('C8:C10', u'FECHA DE VENCIMIENTO O FECHA DE PAGO(1)', format2)
        sheet.merge_range('D8:F8', u'COMPROBANTE DE PAGO O DOCUMENTO', format2)
        sheet.merge_range('D9:D10', u'TIPO (TABLA 10)', format2)
        sheet.merge_range('E9:E10', u'SERIE O CODIGO DE LA DEPENDENCIA ADUANERA (TABLA 11)', format2)
        sheet.merge_range('F9:F10', u'AÑO DE LA EMISION DE LA DUA O DSI', format2)
        sheet.merge_range('G8:G10',
                          u'N° DEL COMPROBANTE DE PAGO, DOCUMENTO, N° DE ORDEN DEL FORMULARIO FISICO O VIRTUAL, N° DE DUA, DSI O LIQUIDACIÓN DE COBRANZA U OTROS DOCUMENTOS EMITIDOS POR SUNAT PARA ACREDITAR EL CREDITO FISCAL EN LA IMPORTACION',
                          format2)
        sheet.merge_range('H8:J8', u'INFORMACIÓN DEL PROVEEDOR', format2)
        sheet.merge_range('H9:I9', u'DOCUMENTO DE IDENTIDAD', format2)
        sheet.write('H10', u'DOCUMENTO DE IDENTIDAD', format2)
        sheet.write('I10', u'NÚMERO', format2)
        sheet.merge_range('J9:J10', u'APELLIDOS Y NOMBRES, DENOMINACION O RAZON SOCIAL', format2)
        sheet.merge_range('K8:L8', u'ADQUISIONES GRAVADAS DESTINADAS A OPERACIONES GRAVADAS Y/O DE EXPORTACION', format2)
        sheet.merge_range('K9:K10', u'BASE IMPONIBLE', format2)
        sheet.merge_range('L9:L10', u'IGV', format2)
        sheet.merge_range('M8:N8', u'ADQUISIONES GRAVADAS DESTINADAS A OPERACIONES GRAVADAS Y/O DE EXPORTACION Y A OPERACIONES NO GRAVADAS',
                          format2)
        sheet.merge_range('M9:M10', u'BASE IMPONIBLE', format2)
        sheet.merge_range('N9:N10', u'IGV', format2)
        sheet.merge_range('O8:P8',
                          u'ADQUISIONES GRAVADAS DESTINADAS A OPERACIONES NO GRAVADAS',
                          format2)
        sheet.merge_range('O9:O10', u'BASE IMPONIBLE', format2)
        sheet.merge_range('P9:P10', u'IGV', format2)
        sheet.merge_range('Q8:Q10', u'VALOR DE LAS ADQUISIONES NO GRAVADAS', format2)
        sheet.merge_range('R8:R10', u'ISC', format2)
        sheet.merge_range('S8:S10', u'OTROS TRIBUTOS Y CARGOS', format2)
        sheet.merge_range('T8:T10', u'IMPORTE TOTAL', format2)
        sheet.merge_range('U8:U10', u'N° DE COMPROBANTE DE PAGO EMITIDO POR SUJETO NO DOMICILIADO (2)', format2)
        sheet.merge_range('V8:X8',
                          u'CONSTANCIA DE DEPOSITO DE DETRACCION (3)',
                          format2)
        sheet.merge_range('V9:V10', u'NÚMERO', format2)
        sheet.merge_range('W9:W10', u'FECHA DE EMISIÓN', format2)
        sheet.merge_range('X9:X10', u'TIPO DE CAMBIO', format2)
        sheet.merge_range('Y8:AB8', u'REFERENCIA DEL COMPROBANTE DE PAGO O DOCUMENTO ORIGINAL QUE SE MODIFICA', format2)
        sheet.merge_range('Y9:Y10', u'FECHA', format2)
        sheet.merge_range('Z9:Z10', u'TIPO (TABLA 10)', format2)
        sheet.merge_range('AA9:AA10', u'SERIE', format2)
        sheet.merge_range('AB9:AB10', u'N° DEL COMPROBANTE DE PAGO O DOCUMENTO', format2)

        # Loop de report_lines
        i = 10
        total_bi1 = total_igv1 = total_bi2 = total_igv2 = total_bi3 = total_igv3 = total_vang = total_isc = total_otc = total_importet = 0
        for invoice in report_lines:
            line = self.env['account.ple.8.1'].search([
                ('cuo_2', '=', invoice.cuo_invoice)
            ], limit=1)
            sheet.write(i, 0, line.cuo_2, format3)
            sheet.write(i, 1, line.fecha_e_4, format3)
            sheet.write(i, 2, line.fecha_v_5, format3)
            sheet.write(i, 3, line.tipo_cpbt_6, format3)
            sheet.write(i, 4, line.serie_cpbt_7, format3)
            sheet.write(i, 5, line.anio_emision_dua_dsi_8, format3)
            sheet.write(i, 6, line.numero_cpbt_9, format3)
            sheet.write(i, 7, line.tipo_doc_pro_11, format3)
            sheet.write(i, 8, line.numero_doc_pro_12, format3)
            sheet.write(i, 9, line.razon_social_pro_13, format3)
            sheet.write(i, 10, line.base_adq_gravadas_14, format3)
            sheet.write(i, 11, line.monto_igv_1_15, format3)
            sheet.write(i, 12, line.base_adq_no_gravadas_16, format3)
            sheet.write(i, 13, line.monto_igv_2_17, format3)
            sheet.write(i, 14, line.base_adq_sin_df_18, format3)
            sheet.write(i, 15, line.monto_igv_3_19, format3)
            sheet.write(i, 16, line.valor_adq_no_gravadas_20, format3)
            sheet.write(i, 17, line.monto_isc_21, format3)
            sheet.write(i, 18, line.otros_conceptos_22, format3)
            sheet.write(i, 19, line.importe_total_23, format3)
            sheet.write(i, 20, "x", format3)
            sheet.write(i, 21, line.numero_cdd_32, format3)
            sheet.write(i, 22, line.fecha_emision_cdd_31, format3)
            sheet.write(i, 23, line.tipo_cambio_25, format3)
            sheet.write(i, 24, line.fecha_emision_doc_mod_26, format3)
            sheet.write(i, 25, line.tipo_cpbt_mod_27, format3)
            sheet.write(i, 26, line.serie_cpbt_mod_28, format3)
            sheet.write(i, 27, line.numero_cpbt_mod_30, format3)
            i += 1
            total_bi1 += float(line.base_adq_gravadas_14)
            total_igv1 += float(line.monto_igv_1_15)
            total_bi2 += float(line.base_adq_no_gravadas_16)
            total_igv2 += float(line.monto_igv_2_17)
            total_bi3 += float(line.base_adq_sin_df_18)
            total_igv3 += float(line.monto_igv_3_19)
            total_vang += float(line.valor_adq_no_gravadas_20)
            total_isc += float(line.monto_isc_21)
            total_otc += float(line.otros_conceptos_22)
            total_importet += float(line.importe_total_23)
        total_i = i + 1

        # Filas de sumas
        # Totales
        sheet.write('J' + str(total_i), u'TOTALES', format2)
        sheet.write('K' + str(total_i), total_bi1, format_footer)
        sheet.write('L' + str(total_i), total_igv1, format_footer)
        sheet.write('M' + str(total_i), total_bi2, format_footer)
        sheet.write('N' + str(total_i), total_igv2, format_footer)
        sheet.write('O' + str(total_i), total_bi3, format_footer)
        sheet.write('P' + str(total_i), total_igv3, format_footer)
        sheet.write('Q' + str(total_i), total_vang, format_footer)
        sheet.write('R' + str(total_i), total_isc, format_footer)
        sheet.write('S' + str(total_i), total_otc, format_footer)
        sheet.write('T' + str(total_i), total_importet, format_footer)

    def get_report_140100(self,workbook,data):
        reporte_ple = self.env['report.biosis_cont_report.report_ple']
        libro_electronico = self.env['biosis_cont_report.libro.electronico'].search(
            [('id', '=', data['libro_electronico'][0])], limit=1)
        filename, filename_v, filecontent = reporte_ple.generate_txt_report(data['mes'], data['year'], data['tipo_reporte'], data['used_context']['company'])
        report_name = libro_electronico.nro_orden
        """Fechas para seleccion de invoices
        """
        date1 = str(data['year']) + '-' + str(data['mes']) + '-' + '01'
        fecha_inicio = datetime.datetime.strptime(date1, "%Y-%m-%d").date()
        date2 = "%s-%s-%s" % (
        fecha_inicio.year, fecha_inicio.month, calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1])
        fecha_fin = datetime.datetime.strptime(date2, "%Y-%m-%d").date()

        report_lines = self.env['account.invoice'].search([
            ('date_invoice', '>=', fecha_inicio),
            ('date_invoice', '<=', fecha_fin),
            ('type', '=', 'out_invoice'),
            ('state', '!=', 'draft'),
            ('tipo_comprobante_id.code', 'in', ['01', '03', '07', '08']),
            ('company_id', '=', data['used_context']['company']),
            ('ple_generado', '=', True)
        ]).sorted(key=lambda r: r.date_invoice)

        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])
        self.get_report_header(libro_electronico, workbook, sheet, data)
        format1 = workbook.add_format(
            {'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'text_wrap': True,
             'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_sumas = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_saldos = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_inv = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#e4fff6'})
        format_nat = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f9f7f7'})
        format_fun = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f8d9d9'})
        format_footer = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#ccff33'})

        # Especificamos ancho de columnas
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 15)
        sheet.set_column('R:R', 15)
        sheet.set_column('S:S', 15)
        sheet.set_column('T:T', 15)
        sheet.set_column('U:U', 15)
        sheet.set_column('V:V', 15)

        # Definimos alto filas
        sheet.set_row(7, 43)
        sheet.set_row(9, 87)
        # Definimos la cabecera del reporte
        sheet.merge_range('A8:A10', u'NUMERO CORRELATIVO DEL REGISTRO O CODIGO UNICO DE LA OPERACION', format2)
        sheet.merge_range('B8:B10', u'FECHA DE EMISION DEL COMPROBANTE DE PAGO O DOCUMENTO', format2)
        sheet.merge_range('C8:C10', u'FECHA DE VENCIMIENTO O FECHA DE PAGO(1)', format2)
        sheet.merge_range('D8:F8', u'COMPROBANTE DE PAGO O DOCUMENTO', format2)
        sheet.merge_range('D9:D10', u'TIPO (TABLA 10)', format2)
        sheet.merge_range('E9:E10', u'N° DE SERIE O N° DE SERIE DE LA MAQUINA REGISTRADORA', format2)
        sheet.merge_range('F9:F10', u'NUMERO', format2)
        sheet.merge_range('G8:I8', u'INFORMACIÓN DEL CLIENTE', format2)
        sheet.merge_range('G9:H9', u'DOCUMENTO DE IDENTIDAD', format2)
        sheet.write('G10', u'TIPO (TABLA 2)', format2)
        sheet.write('H10', u'NÚMERO', format2)
        sheet.merge_range('I9:I10', u'APELLIDOS Y NOMBRES, DENOMINACION O RAZON SOCIAL', format2)
        sheet.merge_range('J8:J10', u'VALOR FACTURADO DE LA EXPORTACION',
                          format2)
        sheet.merge_range('K8:K10', u'BASE IMPONIBLE DE LA OPERACION GRAVADA', format2)
        sheet.merge_range('L8:M8', u'IMPORTE TOTAL DE LA OPERACION EXONERADA O INAFECTA', format2)
        sheet.merge_range('L9:L10', u'EXONERADA', format2)
        sheet.merge_range('M9:M10', u'INAFECTA', format2)
        sheet.merge_range('N8:N10', u'ISC', format2)
        sheet.merge_range('O8:O10', u'IGV Y/O IPM', format2)
        sheet.merge_range('P8:P10', u'OTROS TRIBUTOS Y CARGOS QUE NO FORMAN PARTE DE LA BASE IMPONIBLE', format2)
        sheet.merge_range('Q8:Q10', u'IMPORTE TOTAL DEL COMPROBANTE DE PAGO', format2)
        sheet.merge_range('R8:R10', u'TIPO DE CAMBIO', format2)
        sheet.merge_range('S8:V8', u'REFERENCIA DEL COMPROBANTE DE PAGO O DOCUMENTO ORIGINAL QUE SE MODIFICA', format2)
        sheet.merge_range('S9:S10', u'FECHA', format2)
        sheet.merge_range('T9:T10', u'TIPO (TABLA 10)', format2)
        sheet.merge_range('U9:U10',
                          u'SERIE',
                          format2)
        sheet.merge_range('V9:V10', u'N° DEL COMPROBANTE DE PAGO O DOCUMENTO', format2)

        # Loop de report_lines
        i = 10
        total_vfx = total_biog = total_ioe = total_ioi = total_isc = total_igv = total_otc = total_importet = 0
        for invoice in report_lines:
            line = self.env['account.ple.14.1'].search([
                ('cuo_2', '=', invoice.cuo_invoice)
            ], limit=1)
            sheet.write(i, 0, line.cuo_2, format3)
            sheet.write(i, 1, line.fecha_e_4, format3)
            sheet.write(i, 2, line.fecha_v_5, format3)
            sheet.write(i, 3, line.tipo_cpbt_6, format3)
            sheet.write(i, 4, line.serie_cpbt_7, format3)
            sheet.write(i, 5, line.numero_cpbt_8, format3)
            sheet.write(i, 6, line.tipo_doc_pro_10, format3)
            sheet.write(i, 7, line.numero_doc_pro_11, format3)
            sheet.write(i, 8, line.razon_social_pro_12, format3)
            sheet.write(i, 9, line.valor_facturado_13, format3)
            sheet.write(i, 10, line.base_adq_gravadas_14, format3)
            sheet.write(i, 11, line.importe_operacion_exonerada_18, format3)
            sheet.write(i, 12, line.importe_operacion_inafecta_19, format3)
            sheet.write(i, 13, line.isc_20, format3)
            sheet.write(i, 14, line.monto_igv_16, format3)
            sheet.write(i, 15, line.otros_conceptos_23, format3)
            sheet.write(i, 16, line.importe_total_24, format3)
            sheet.write(i, 17, line.tipo_cambio_26, format3)
            sheet.write(i, 18, line.fecha_emision_doc_mod_27, format3)
            sheet.write(i, 19, line.tipo_cpbt_mod_28, format3)
            sheet.write(i, 20, line.serie_cpbt_mod_29, format3)
            sheet.write(i, 21, line.numero_cpbt_mod_codigo_dep_aduanera_30, format3)
            i += 1
            total_vfx += float(line.valor_facturado_13)
            total_biog += float(line.base_adq_gravadas_14)
            total_ioe += float(line.importe_operacion_exonerada_18)
            total_ioi += float(line.importe_operacion_inafecta_19)
            total_isc += float(line.isc_20)
            total_igv += float(line.monto_igv_16)
            total_otc += float(line.otros_conceptos_23)
            total_importet += float(line.importe_total_24)
        total_i = i + 1

        # Filas de sumas
        # Totales
        sheet.write('I' + str(total_i), u'TOTALES', format2)
        sheet.write('J' + str(total_i), total_vfx, format_footer)
        sheet.write('K' + str(total_i), total_biog, format_footer)
        sheet.write('L' + str(total_i), total_ioe, format_footer)
        sheet.write('M' + str(total_i), total_ioi, format_footer)
        sheet.write('N' + str(total_i), total_isc, format_footer)
        sheet.write('O' + str(total_i), total_igv, format_footer)
        sheet.write('P' + str(total_i), total_otc, format_footer)
        sheet.write('Q' + str(total_i), total_importet, format_footer)

    def get_report_050100(self,workbook,data):
        reporte_ple = self.env['report.biosis_cont_report.report_ple']
        libro_electronico = self.env['biosis_cont_report.libro.electronico'].search(
            [('id', '=', data['libro_electronico'][0])], limit=1)
        filename, filename_v, filecontent = reporte_ple.generate_txt_report(data['mes'], data['year'], data['tipo_reporte'], data['used_context']['company'])
        report_name = libro_electronico.nro_orden

        #Fechas para seleccion de lineas de diario
        if data['por_rango']:
            date1 = str(data['year']) + '-' + str(data['mes']) + '-' + '01'
            fecha_inicio = datetime.datetime.strptime(date1, "%Y-%m-%d").date()
            date2 = "%s-%s-%s" % (
                fecha_inicio.year, fecha_inicio.month, calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1])
            fecha_fin = datetime.datetime.strptime(date2, "%Y-%m-%d").date()

            report_lines = self.env['account.ple.5.1'].search([
                ('fecha_c_13', '>=', fecha_inicio),
                ('fecha_c_13', '<=', fecha_fin),
                ('company_id','=',data['used_context']['company'])
            ])
        elif data['por_mes']:
            periodo = str(data['year'])+('0'+data['mes'] if len(data['mes'])==1 else data['mes'])+"00"
            report_lines = self.env['account.ple.5.1'].search([
                ('periodo_1', '=', periodo),
                ('company_id', '=', data['used_context']['company'])
            ])
        else:
            periodo = str(data['year'])+"12"+"31"
            report_lines = self.env['account.ple.5.1'].search([
                ('periodo_1', '=', periodo),
                ('company_id', '=', data['used_context']['company'])
            ])
        #List of moves
        move_list = []
        for line in report_lines:
            if line.move_line_id.move_id not in move_list:
                move_list.append(line.move_line_id.move_id)
        move_list.sort(key=lambda r: r.journal_id.id)

        #List of journals
        journal_list = []
        for move in move_list:
            if move.journal_id not in journal_list:
                journal_list.append(move.journal_id)
        journal_list.sort(key=lambda r: r.id)

        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])
        self.get_report_header(libro_electronico, workbook, sheet, data)
        #Definimos formatos para celdas
        format1 = workbook.add_format({'font_size': 12, 'align': 'justify', 'valign': 'vcenter', 'border': 1, 'bold': True})
        format2 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'text_wrap': True,
             'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_sumas = workbook.add_format(
            {'font_size': 10, 'align': 'justify', 'valign': 'vcenter', 'border': 1, 'bold': True})
        format_saldos = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_inv = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#e4fff6'})
        format_nat = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f9f7f7'})
        format_fun = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f8d9d9'})
        format_footer = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#ccff33'})

        # Especificamos ancho de columnas
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 50)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)

        # Definimos alto filas
        sheet.set_row(7, 43)
        sheet.set_row(9, 87)
        # Definimos la cabecera del reporte
        sheet.merge_range('A8:A10', u'NUMERO CORRELATIVO DEL ASIENTO O CODIGO UNICO DE LA OPERACION', format2)
        sheet.merge_range('B8:B10', u'FECHA DE LA OPERACION', format2)
        sheet.merge_range('C8:C10', u'GLOSA O DESCRIPCIÓN DE LA OPERACIÓN', format2)
        sheet.merge_range('D8:F8', u'REFERENCIA DE LA OPERACIÓN', format2)
        sheet.merge_range('D9:D10', u'CÓDIGO DEL LIBRO O REGISTRO (TABLA 8)', format2)
        sheet.merge_range('E9:E10', u'NÚMERO CORRELATIVO', format2)
        sheet.merge_range('F9:F10', u'NÚMERO DEL DOCUMENTO SUSTENTATORIO', format2)
        sheet.merge_range('G8:H8', u'CUENTA CONTABLE ASOCIADA A LA OPERACIÓN', format2)
        sheet.merge_range('G9:G10', u'CÓDIGO', format2)
        sheet.merge_range('H9:H10', u'DENOMINACIÓN', format2)
        sheet.merge_range('I8:J8', u'MOVIMIENTO', format2)
        sheet.merge_range('I9:I10', u'DEBE', format2)
        sheet.merge_range('J9:J10', u'HABER', format2)
        # Loop de report_lines
        i = 10
        total_debe = total_haber  = 0
        for journal in journal_list:
            total_sub_debe = 0
            total_sub_haber = 0
            sheet.merge_range('A'+str(i+1)+':J'+str(i+1), 'Subdiario: '+journal.name, format1)
            i = i+1
            for line in [line for line in report_lines if line.move_line_id.move_id.journal_id == journal]:
                sheet.write(i, 0, line.cuo_2, format3)
                sheet.write(i, 1, line.move_line_id.move_id.date, format3)
                sheet.write(i, 2, line.move_line_id.move_id.name, format3)
                sheet.write(i, 3, "por implementar", format3)
                sheet.write(i, 4, line.move_line_id.invoice_id.numero_comprobante if line.move_line_id.invoice_id else "", format3)
                sheet.write(i, 5, line.fecha_c_13, format3)
                sheet.write(i, 6, line.move_line_id.account_id.code, format3)
                sheet.write(i, 7, line.move_line_id.account_id.name, format3)
                sheet.write(i, 8, str(line.move_line_id.debit), format3)
                sheet.write(i, 9, str(line.move_line_id.credit), format3)
                total_sub_debe = total_sub_debe + line.move_line_id.debit
                total_sub_haber = total_sub_haber + line.move_line_id.credit
                i += 1
            sheet.write(i,7,"TOTAL SUBDIARIO",format_sumas)
            sheet.write(i,8,str(total_sub_debe),format_sumas)
            sheet.write(i,9,str(total_sub_haber),format_sumas)
            total_debe = total_debe + total_sub_debe
            total_haber = total_haber + total_sub_haber
            i = i + 1
        sheet.write(i, 7, "TOTAL", format_sumas)
        sheet.write(i, 8, str(total_debe), format_sumas)
        sheet.write(i, 9, str(total_haber), format_sumas)


    def get_report_060100(self,workbook,data):
        reporte_ple = self.env['report.biosis_cont_report.report_ple']
        libro_electronico = self.env['biosis_cont_report.libro.electronico'].search(
            [('id', '=', data['libro_electronico'][0])], limit=1)
        filename, filename_v, filecontent = reporte_ple.generate_txt_report(data['mes'], data['year'], data['tipo_reporte'], data['used_context']['company'])
        report_name = libro_electronico.nro_orden
        # Fechas para seleccion de lineas de diario
        if data['por_rango']:
            date1 = str(data['year']) + '-' + str(data['mes']) + '-' + '01'
            fecha_inicio = datetime.datetime.strptime(date1, "%Y-%m-%d").date()
            date2 = "%s-%s-%s" % (
                fecha_inicio.year, fecha_inicio.month, calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1])
            fecha_fin = datetime.datetime.strptime(date2, "%Y-%m-%d").date()

            report_lines = self.env['account.ple.6.1'].search([
                ('fecha_c_13', '>=', fecha_inicio),
                ('fecha_c_13', '<=', fecha_fin),
                ('company_id', '=', data['used_context']['company'])
            ])
        elif data['por_mes']:
            periodo = str(data['year']) + ('0' + data['mes'] if len(data['mes']) == 1 else data['mes']) + "00"
            report_lines = self.env['account.ple.6.1'].search([
                ('periodo_1', '=', periodo),
                ('company_id', '=', data['used_context']['company'])
            ])
        else:
            periodo = str(data['year']) + "12" + "31"
            report_lines = self.env['account.ple.6.1'].search([
                ('periodo_1', '=', periodo),
                ('company_id', '=', data['used_context']['company'])
            ])

        # List of moves
        account_list = []
        for line in report_lines:
            if line.move_line_id.account_id not in account_list:
                account_list.append(line.move_line_id.account_id)
        account_list.sort(key=lambda r: int(r.code))

        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])
        self.get_report_header(libro_electronico, workbook, sheet, data)
        # Definimos formatos para celdas
        format1 = workbook.add_format(
            {'font_size': 8, 'align': 'justify', 'valign': 'vcenter', 'border': 1, 'bold': True})
        format2 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'text_wrap': True,
             'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        #format_sumas = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_sumas = workbook.add_format(
            {'font_size': 10, 'align': 'justify', 'valign': 'vcenter', 'border': 1, 'bold': True})
        format_saldos = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_inv = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#e4fff6'})
        format_nat = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f9f7f7'})
        format_fun = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f8d9d9'})
        format_footer = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#ccff33'})

        # Especificamos ancho de columnas
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 60)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)

        # Definimos alto filas
        sheet.set_row(7, 43)

        # Definimos la cabecera del reporte
        sheet.merge_range('A8:A9', u'FECHA DE LA OPERACIÓN', format2)
        sheet.merge_range('B8:B9', u'NUMERO CORRELATIVO DEL LIBRO DIARIO', format2)
        sheet.merge_range('C8:C9', u'DESCRIPCIÓN O GLOSA DE LA OPERACIÓN', format2)
        sheet.merge_range('D8:E8', u'SALDOS Y MOVIMIENTOS', format2)
        sheet.write('D9', u'DEUDOR', format2)
        sheet.write('E9', u'ACREEDOR', format2)

        # Loop de report_lines
        i = 9
        total_deudor = total_acreedor = 0
        for account in account_list:
            total_sub_debe = 0
            total_sub_haber = 0
            sheet.merge_range('A' + str(i + 1) + ':E' + str(i + 1), account.code+ '-' + account.name, format1)
            i = i + 1
            for line in [line for line in report_lines if line.move_line_id.account_id == account]:
                sheet.write(i, 0, line.fecha_c_13, format3)
                sheet.write(i, 1, line.cuo_2+"-"+line.move_cuo_3, format3)
                sheet.write(i, 2, line.glosa_16, format3)
                sheet.write(i, 3, line.mov_debe_18, format3)
                sheet.write(i, 4, line.mov_haber_19, format3)
                total_sub_debe += float(line.mov_debe_18)
                total_sub_haber += float(line.mov_haber_19)
                i += 1
            sheet.write(i, 2, "TOTAL CUENTA", format_sumas)
            sheet.write(i, 3, str(total_sub_debe), format_sumas)
            sheet.write(i, 4, str(total_sub_haber), format_sumas)
            total_deudor = total_deudor + total_sub_debe
            total_acreedor = total_acreedor + total_sub_haber
            i = i + 1
        # Filas de sumas Totales
        sheet.write('C' + str(i), u'TOTALES', format2)
        sheet.write('D' + str(i), total_deudor, format_footer)
        sheet.write('E' + str(i), total_acreedor, format_footer)


    def get_report_header(self,libro_electronico,workbook,sheet,data):
        format1 = workbook.add_format({'font_size': 14, 'align': 'justify', 'valign': 'vcenter', 'bold': True})

        if data['por_rango']:
            periodo = datetime.datetime.strptime(data['date_from'],'%Y-%m-%d').strftime('%d/%m/%Y')+' - '+datetime.datetime.strptime(data['date_to'],'%Y-%m-%d').strftime('%d/%m/%Y')
        elif data['por_mes']:
            periodo = MES_SPA.get(str(data['mes']))+' - '+str(data['year'])
        else:
            periodo = str(data['year'])

        company = self.env['res.company'].search([('id', '=', data['used_context']['company'])], limit=1)
        numero_documento = company.partner_id.vat
        company_name = company.partner_id.name
        # Especificamos cabecera
        sheet.merge_range('A1:L1', u'FORMATO '+libro_electronico.nro_orden+': '+libro_electronico.name, format1)
        sheet.merge_range('A3:L3', u'PERIODO' + ': ' + periodo, format1)
        sheet.merge_range('A4:L4', u'RUC' + ': ' + numero_documento, format1)
        sheet.merge_range('A5:L5', u'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: ' + company_name, format1)

    def get_sum_accounts(self, bc_lines, item_type, sum_accounts, minus_accounts=None):
        total = 0
        pattern_10 = re.compile("10")
        pattern_40 = re.compile("40")
        pattern_sum = re.compile(sum_accounts)
        if minus_accounts:
            pattern_minus = re.compile(minus_accounts)
        for line in bc_lines:
            if sum_accounts:
                if pattern_sum.match(line['codigo']):
                    if item_type == "anc":
                        if pattern_40.match(line['codigo']):
                            if line['balance'] < 0:
                                total = total + abs(line['balance'])
                        else:
                            total = total + line['balance']
                    elif item_type == "pc":
                        if pattern_10.match(line['codigo']):
                            if line['balance'] < 0:
                                total = total + abs(line['balance'])
                        else:
                            total = total + abs(line['balance'])
                    else:
                        total = total + line['balance']
            if minus_accounts:
                if pattern_minus.match(line['codigo']):
                    total = total - line['balance']
        return total