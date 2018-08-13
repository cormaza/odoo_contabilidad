# -*- coding: utf-8 -*-

import datetime
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class BiosisContReportSunatXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, lines):
        reporteador = self.env["account.report.logic"]
        reporteador.get_report_body(workbook,data)
BiosisContReportSunatXlsx('report.biosis_cont_report.report_sunat_xls.xlsx','account.sunatreport')