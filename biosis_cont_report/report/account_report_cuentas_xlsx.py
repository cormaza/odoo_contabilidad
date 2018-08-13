# -*- coding: utf-8 -*-
import datetime
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class BiosisContReportCuentasXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, lines):
        report_name = u'Cuentas'
        desde_fecha = data['date_desde']
        hasta_fecha = data['date_hasta']
        tipo_reporte = data['tipo_reporte']

        lista_partner = []
        if tipo_reporte == 'cpp':
            titulo = u'DOCUMENTOS PENDIENTES POR CLIENTE - CUENTAS X PAGAR'
            lista_partner = self.env['res.partner'].search([
                ('supplier','=',True)
            ])
        elif tipo_reporte == 'cpc':
            titulo = u'DOCUMENTOS PENDIENTES POR CLIENTE - CUENTAS X COBRAR'
            lista_partner = self.env['res.partner'].search([
                ('customer','=',True)
            ])
        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])

        # Formato para celdas
        format1 = workbook.add_format({'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format({'font_size': 11, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'align': 'justify', 'bold': True,})
        format4 = workbook.add_format({'font_size': 10, 'align': 'justify'})
        format5 = workbook.add_format({'font_size': 12, 'align': 'justify','bold': True})
        format_sumas = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_saldos = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1})
        format_inv = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#e4fff6'})
        format_nat = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f9f7f7'})
        format_fun = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#f8d9d9'})
        format_footer = workbook.add_format({'font_size': 10, 'align': 'justify', 'border': 1, 'bg_color': '#ccff33'})

        # Especificamos ancho de columnas
        sheet.set_column('A:A', 50)
        sheet.set_column('B:B', 19)
        sheet.set_column('C:C', 19)
        sheet.set_column('D:D', 19)
        sheet.set_column('E:E', 19)
        sheet.set_column('F:F', 19)
        sheet.set_column('G:G', 19)
        sheet.set_column('H:H', 19)

        tipo_documento = self.env.user.company_id.partner_id.catalog_06_id.name
        numero_documento = self.env.user.company_id.partner_id.vat
        company_name = self.env.user.company_id.partner_id.name
        # Especificamos cabecera
        sheet.merge_range('A1:G1', company_name, format4)
        sheet.write('H1', u'FECHA: '+datetime.datetime.now().strftime('%d/%m/%Y'), format4)
        sheet.merge_range('A2:G2', tipo_documento+': '+numero_documento, format4)
        sheet.write('H2', u'HORA: '+datetime.datetime.now().strftime('%H:%M:%S'), format4)
        sheet.merge_range('A4:H4', titulo, format1)
        sheet.merge_range('A5:H5', u'A LA FECHA '+hasta_fecha, format1)
        sheet.write('A7',u'TIPO DOCUMENTO',format2)
        sheet.write('B7', u'NRO DOCUMENTO', format2)
        sheet.write('C7', u'FECHA DOCUMENTO', format2)
        sheet.write('D7', u'FECHA VENC.', format2)
        sheet.write('E7', u'DIAS VENC.', format2)
        sheet.write('F7', u'MONEDA ORIGEN', format2)
        sheet.write('G7', u'IMPORTE', format2)
        sheet.write('H7', u'SALDO', format2)

        i = 7
        for partner in lista_partner:
            list_invoice = self.env['account.invoice'].search([
                ('partner_id','=',partner.id),
                ('state', '!=', 'draft'),
                ('date_invoice', '>=', desde_fecha),
                ('date_invoice', '<=', hasta_fecha)
            ])
            if len(list_invoice) > 0:
                sheet.merge_range(i,0,i,7,partner.name,format5)
                total_importe = 0
                total_saldo = 0
                i += 1
                for invoice in list_invoice:
                    sheet.write(i, 0, invoice.tipo_documento.name, format4)
                    sheet.write(i, 1, invoice.numero_comprobante, format4)
                    sheet.write(i, 2,datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%d/%m/%Y') if invoice.date_invoice else u'', format4)
                    sheet.write(i, 3, datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime('%d/%m/%Y') if invoice.date_due else u'', format4)
                    sheet.write(i, 4, str.split(str(abs((datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d') - datetime.datetime.now()))))[0], format4)
                    sheet.write(i, 5, u'SOL', format4)
                    sheet.write(i, 6, str(invoice.amount_total), format4)
                    sheet.write(i, 7, str(invoice.residual_company_signed), format4)
                    total_importe += invoice.amount_total
                    total_saldo += invoice.residual_company_signed
                    i += 1

                #Total importe
                sheet.write(i, 6, u'SUB TOTAL: ', format3)
                sheet.write(i, 7, total_saldo, format3)
                i += 1


BiosisContReportCuentasXlsx('report.biosis_cont_report.report_cuentas_xls.xlsx','account.cuentascp')