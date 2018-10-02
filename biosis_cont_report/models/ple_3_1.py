# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class Ple_3_1(models.Model):
    _name = 'account.ple.3.1'
    _description = 'PLE para ESTADO DE SITUACIÓN FINANCIERA'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cod_catalogo_2 = fields.Char(string=u'Código del Catálogo', required=True)
    cod_rubro_3 = fields.Char(string=u'Código del Rubro del Estado Financiero', required=True)
    saldo_rubro_4 = fields.Char(string=u'Saldo del Rubro Contable', required=True)
    estado_5 = fields.Char(string=u'Estado', required=True)
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.cod_catalogo_2 + '|' + self.cod_rubro_3 + '|' + self.saldo_rubro_4 + '|' \
               + self.estado_5 + '|' + '\n'


    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_ef_res = ''
        fecha_reporte_anio = str(fecha_fin.year) + '12' + '31'
        ef_ple_list = []
        ef_ple_update = []
        ef_ple_old = []
        ef_ple_new = []

        bc_report = self.get_lines_report(company_id, fecha_inicio, fecha_fin)  # Lineas de bc segun el periodo ingresado

        ef_ple_list = self.env['account.ple.3.1'].search([
            ('periodo_1', '=', fecha_reporte_anio),
            ('company_id', '=', company_id.id)
        ])

        ef_procesadas = self.get_ef_lines(bc_report)

        if len(ef_ple_list) > 0:
            for line_ef in ef_procesadas:
                for line_ple in ef_ple_list:
                    if line_ple.cod_rubro_3 == line_ef['codigo_s_f']:
                        if line_ple.saldo_rubro_4 != ((str(line_ef['saldo_rubro']) if line_ef['saldo_rubro'] > 0 else '0.00')):
                            ef_ple_update.append(line_ef)
                        else:
                            ef_ple_old.append(line_ef)
                        continue
        else:
            ef_ple_new = ef_procesadas

        if len(ef_ple_list) > 0:
            for line_ef in ef_procesadas:
                if not (line_ef in ef_ple_update) and not (line_ef in ef_ple_old):
                    ef_ple_new.append(line_ef)

        if len(ef_ple_new) == 0 and len(ef_ple_list) == 0:
            # warning = {
            #    'title': _('Alerta!'),
            #    'message': _('No hay movimientos para el periodo/rango seleccionado!'),
            # }
            return ' '
        else:
            if len(ef_ple_new) > 0:
                """
                   Pasos para agregar lineas BC al res
                """
                ple_nuevos = self.create_ple_items(company_id, ef_ple_new, fecha_reporte, fecha_inicio, fecha_fin)
                ple_ef_res = ple_ef_res + ple_nuevos

            if len(ef_ple_list) > 0:
                """
                    Pasos para crear lineas Diario Detalle con cuentas_list_new
                 """
                ple_old = self.update_ple_items(company_id, ef_ple_old, ef_ple_update, fecha_reporte, fecha_inicio, fecha_fin)
                ple_ef_res = ple_ef_res + ple_old

            return ple_ef_res

    @api.multi
    def create_ple_items(self, company_id, ef_ple_new, fecha_reporte,fecha_inicio,fecha_fin):
        ple_items = ''
        ple_ef = self.env['account.ple.3.1']
        periodo = str(fecha_fin.year) + '12' + '31'
        for line in ef_ple_new:
            if datetime.date.today() <= self.get_fecha_atraso(fecha_fin):
                ple_item_estado_5 = u'1'
            elif datetime.date.today() > self.get_fecha_atraso(fecha_fin):
                ple_item_estado_5 = u'8'
            ple_item_vals = {
                'periodo_1': periodo,
                'cod_catalogo_2': line['codigo'],
                'cod_rubro_3': line['codigo_s_f'],  # implementar
                'saldo_rubro_4': str(line['saldo_rubro']) if line['saldo_rubro'] > 0 else '0.00',
                'estado_5': ple_item_estado_5,
                'company_id': company_id.id
            }
            ple_item = ple_ef.create(ple_item_vals)
            # despues de proceso
            ple_items = ple_items + ple_item.get_ple_line()
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, ef_ple_old, ef_ple_update, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        for line in ef_ple_old:
            ple_item = self.env['account.ple.3.1'].search([
                ('cod_rubro_3', '=', line['codigo_s_f'])
            ], limit=1)
            ple_items = ple_items + ple_item.get_ple_line()

        for line in ef_ple_update:
            ple_item = self.env['account.ple.3.1'].search([
                ('cod_rubro_3', '=', line['codigo_s_f'])
            ], limit=1)
            estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'

            ple_item_vals = {
                'saldo_rubro_4': str(line['saldo_rubro']) if line['saldo_rubro'] > 0 else '0.00',
                'estado_19': estado_ple,
                'company_id': company_id.id
            }
            ple_item.write(ple_item_vals)
            ple_items = ple_items + ple_item.get_ple_line()

        return ple_items

    def get_lines_report(self, company_id, fecha_inicio, fecha_fin):
        lines = []
        reporte_balance = self.env['report.biosis_cont_report.balance_comprobacion']  # Reporte financiero(odoo)
        libro_electronico = self.env['biosis_cont_report.libro.electronico'].search([('codigo_le', '=', '031700')],
                                                                                    limit=1)
        report_lines = reporte_balance.get_account_lines(
            self.get_data_report(company_id, libro_electronico, fecha_inicio, fecha_fin))

        for line in report_lines:
            if line['level'] == 4:
                lines.append(line)

        return lines

    def get_data_report(self, company_id, libro_electronico, fecha_inicio, fecha_fin):
        data = {}
        data['account_report_id'] = (libro_electronico.account_report_id.id, libro_electronico.account_report_id.name)
        data['enable_filter'] = False
        data['debit_credit'] = True
        data['used_context'] = {}
        data['used_context']['date_from'] = fecha_inicio.strftime('%Y-%m-%d')
        data['used_context']['date_to'] = fecha_fin.strftime('%Y-%m-%d')
        data['used_context']['lang'] = u'es_PE'
        data['used_context']['state'] = u'posted'
        data['used_context']['strict_range'] = True
        data['used_context']['company'] = company_id.id
        return data

    def get_fecha_atraso(self, fecha_fin):
        grupo_libro = self.env['biosis_cont_report.grupolibroelectronico'].search([
            ('code', '=', '3')
        ], limit=1)
        if grupo_libro.type_time == 'MES':
            fecha_maxima = fecha_fin + relativedelta(months=int(grupo_libro.quantity))
        else:
            fecha_maxima = fecha_fin + relativedelta(days=int(grupo_libro.quantity))
        return fecha_maxima


    def get_ef_lines(self,bc_lines):
        catalogo_financiero = self.env['biosis.report.ple.anexo3.tabla22'].search([
            ('num_order','=','01')
        ], limit=1)
        ef_lines = self.env['biosis.report.ple.anexo3.tabla34'].search([
            ('estado_financiero_id','=',catalogo_financiero.id),
            ('codigo_le','=','030100')
        ])
        ef_lines_res = []
        for line in ef_lines:
            ef_line = {}
            ef_line['codigo'] = line.estado_financiero_id.num_order
            ef_line['codigo_s_f'] = line.codigo
            ef_line['tipo'] = line.tipo
            ef_line['padre'] = line.padre
            if line.tipo == 'cuenta':
                total_ef = 0
                if line.cuentas:
                    cuentas = re.compile(line.cuentas)
                if line.excepciones:
                    cuentas_exclude = re.compile(line.excepciones)

                for line_bc in bc_lines:
                    if line.cuentas:
                        if cuentas.match(line_bc['codigo']):
                            total_ef = total_ef + line_bc['balance']
                    if line.excepciones:
                        if cuentas_exclude.match(line_bc['codigo']):
                            total_ef = total_ef - line_bc['balance']
                ef_line['saldo_rubro'] = total_ef
            else:
                ef_line['saldo_rubro'] = 0
            ef_lines_res.append(ef_line)

        copy_ef_lines_res = list(ef_lines_res)
        for line in ef_lines_res:
            if line['tipo'] == 'suma':
                line['saldo_rubro'] = self.get_ef_child_sum(line,copy_ef_lines_res)

        return ef_lines_res


    def get_ef_child_sum(self, parent_ef, ef_lines_res):
        suma_saldo = 0
        for line in ef_lines_res:
            if line['padre'] == parent_ef['codigo_s_f']:
                suma_saldo = suma_saldo + line['saldo_rubro']
        return suma_saldo
        







