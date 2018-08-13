# -*- coding: utf-8 -*-
import datetime
import calendar
from odoo import api, models

class BiosisContReportDetracciones(models.AbstractModel):
    _name = 'report.biosis_cont_report.report_pago_detracciones'

    def generate_txt_report(self,mes_int,year_int,tipo_r):
        #Obtener fechas de busqueda
        year = str(year_int)
        mes = str(mes_int)
        periodo = year+mes
