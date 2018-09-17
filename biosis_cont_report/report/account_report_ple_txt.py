# -*- coding: utf-8 -*-
import datetime
import calendar
from odoo import api, models

TIPO_REPORTE_SUNAT = {
    '010100':u'010100',
    '010200':u'010200',
    '030100':u'030100',
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
    '031700':u'031700',
    '031800':u'031800',
    '031900':u'031900',
    '032000':u'032000',
    '032300':u'032300',
    '032400':u'032400',
    '032500':u'032500',
    '040100':u'040100',
    '050100':u'050100',
    '050300':u'050300',
    '050200':u'050200',
    '050400':u'050400',
    '060100':u'060100',
    '070100':u'070100',
    '070300':u'070300',
    '070400':u'070400',
    '080100':u'080100',
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
    '140100':u'140100',
    '140200':u'140200'
}

class BiosisContReportPLE(models.AbstractModel):
    _name = 'report.biosis_cont_report.report_ple'
    def generate_txt_report(self,mes_int,year_int,tipo_r,compania):
        #Obtener fechas de busqueda
        year = str(year_int)
        company_id = self.env['res.company'].search([('id', '=', compania)], limit=1)
        if mes_int != 'False':
            mes = str(mes_int)
        else:
            mes = '01'
        date1 = year+'-'+mes+'-'+'01'
        fecha_inicio = datetime.datetime.strptime(date1,"%Y-%m-%d").date()

        if mes_int != 'False':
            date2 = "%s-%s-%s" % (fecha_inicio.year,fecha_inicio.month,calendar.monthrange(fecha_inicio.year,fecha_inicio.month)[1])
        else:
            date2 = "%s-%s-%s" % (fecha_inicio.year, 12, calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1])
        fecha_fin = datetime.datetime.strptime(date2,"%Y-%m-%d").date()

        company_name = company_id.partner_id.vat
        fecha_reporte = year+('0'+mes if len(mes)==1 else mes)+'00'

        if tipo_r == TIPO_REPORTE_SUNAT['010100']:
            nombre_ple = u'LE' + company_name + year + ('0' + mes if len(mes) == 1 else mes) + u'00' + u'010100' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.1.1'].get_ple(company_id, fecha_reporte, fecha_inicio,fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['010200']:
            nombre_ple = u'LE' + company_name + year + ('0' + mes if len(mes) == 1 else mes) + u'00' + u'010200' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.1.2'].get_ple(company_id, fecha_reporte, fecha_inicio,fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030100']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030100' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.1'].get_ple(company_id, fecha_reporte, fecha_inicio,fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030200']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030200' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.2'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030300']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030300' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.3'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030400']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030400' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.4'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030500']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030500' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.5'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030600']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030600' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.6'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030700']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030700' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.7'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030800']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030800' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.8'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['030900']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'030900' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.9'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['080100']:
            nombre_ple = u'LE' + company_name + year + ('0'+mes if len(mes)==1 else mes) + u'00' + u'080100' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.8.1'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['080200']:
            nombre_ple = u'LE' + company_name + year + ('0'+mes if len(mes)==1 else mes) + u'00' + u'080200' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.8.2'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['080300']:
            nombre_ple = u'LE' + company_name + year + ('0'+mes if len(mes)==1 else mes) + u'00' + u'080300' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.8.3'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['140100']:
            nombre_ple = u'LE' + company_name + year + ('0'+mes if len(mes)==1 else mes) + u'00' + u'140100' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.14.1'].get_ple(company_id, fecha_reporte,fecha_inicio,fecha_fin)

        elif tipo_r == TIPO_REPORTE_SUNAT['031100']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'031100' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.11'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['031200']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'031200' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.12'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['031300']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'031300' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.13'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['031700']:
            nombre_ple = u'LE' + company_name + year + u'12' + u'31' + u'031700' + u'01' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.3.17'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['050100']:
            nombre_ple = u'LE' + company_name + year + ('0'+mes if len(mes)==1 else mes) + u'00' + u'050100' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.5.1'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['050300']:
            nombre_ple = u'LE' + company_name + year + ('0' + mes if len(mes) == 1 else mes) + u'00' + u'050300' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.5.3'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)
        elif tipo_r == TIPO_REPORTE_SUNAT['060100']:
            nombre_ple = u'LE' + company_name + year + ('0'+mes if len(mes) == 1 else mes) + u'00' + u'060100' + u'00' + u'1111'
            nombre_ple_v = False
            return nombre_ple, nombre_ple_v, self.env['account.ple.6.1'].get_ple(company_id, fecha_reporte, fecha_inicio, fecha_fin)