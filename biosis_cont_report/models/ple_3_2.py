# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_2(models.Model):
    _name = 'account.ple.3.2'
    _description = u'PLE - DETALLE DEL SALDO DE LA CUENTA 10 EFECTIVO Y EQUIVALENTES DE EFECTIVO (PCGE)'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    codigo_cuenta_2 = fields.Char(string=u'Código del Catálogo', required=True)
    codigo_ef_3 = fields.Char(string=u'Código del Rubro del Entidad Financiero', required=True)
    numero_doc_ef_4 = fields.Char(string=u'Número de la cuenta de la Entidad Financiera', default=u'')
    codigo_moneda_5 = fields.Char(string=u'Código Moneda', default=u'0.000')
    mov_debe_6 = fields.Char(string=u'Movimiento del Debe', required=True)
    mov_haber_7 = fields.Char(string=u'Movimiento del Haber', required=True)
    estado_8 = fields.Char(string=u'Estado', required=True)
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.codigo_cuenta_2 + '|' + self.codigo_ef_3 + '|' + self.numero_doc_ef_4 + '|' + self.codigo_moneda_5 + '|' \
               + self.mov_debe_6 + '|' + self.mov_haber_7 + '|' + self.estado_8 + '|' + '\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_32_res = ''
        fecha_reporte_anio = str(fecha_fin.year) + '12' + '31'
        ple_32_list = []
        ple_32_update = []
        ple_32_old = []
        ple_32_new = []

        bc_report = self.get_lines_report(company_id, fecha_inicio, fecha_fin)

        ple_32_list = self.env['account.ple.3.2'].search([
            ('periodo_1', '=', fecha_reporte_anio),
            ('company_id', '=', company_id.id)
        ])

        procesadas_32 = self.get_32_lines(bc_report)

        if len(ple_32_list) > 0:
            for line_ef in procesadas_32:
                for line_ple in ple_32_list:
                    if line_ple.codigo_cuenta_2 == line_ef['codigo']:
                        if line_ple.mov_debe_6 != ((str(line_ef['debit']) if line_ef['debit'] > 0 else '0.00')) or \
                                        line_ple.mov_haber_7 != ((str(line_ef['credit']) if line_ef['credit'] > 0 else '0.00')):
                            ple_32_update.append(line_ef)
                        else:
                            ple_32_old.append(line_ef)
                        continue
        else:
            ple_32_new = procesadas_32

        if len(ple_32_list) > 0:
            for line_ef in procesadas_32:
                if not (line_ef in ple_32_update) and not (line_ef in ple_32_old):
                    ple_32_new.append(line_ef)

        if len(ple_32_new) == 0 and len(ple_32_list) == 0:
            # warning = {
            #    'title': _('Alerta!'),
            #    'message': _('No hay movimientos para el periodo/rango seleccionado!'),
            # }
            return ' '
        else:
            if len(ple_32_new) > 0:
                """
                   Pasos para agregar lineas BC al res
                """
                ple_nuevos = self.create_ple_items(company_id, ple_32_new, fecha_reporte, fecha_inicio, fecha_fin)
                ple_32_res = ple_32_res + ple_nuevos

            if len(ple_32_list) > 0:
                """
                    Pasos para crear lineas Diario Detalle con cuentas_list_new
                 """
                ple_old = self.update_ple_items(company_id, ple_32_old, ple_32_update, fecha_reporte, fecha_inicio, fecha_fin)
                ple_32_res = ple_32_res + ple_old

            return ple_32_res

    @api.multi
    def create_ple_items(self, company_id, ple_32_new, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_ef = self.env['account.ple.3.2']
        periodo = str(fecha_fin.year) + '12' + '31'
        for line in ple_32_new:
            diario = self.env['account.journal'].search([
                ('type','=','bank'),
                ('default_debit_account_id.code','=',line['codigo']),
                ('company_id','=',company_id.id)
            ], limit=1)
            if datetime.date.today() <= self.get_fecha_atraso(fecha_fin):
                ple_item_estado_8 = u'1'
            elif datetime.date.today() > self.get_fecha_atraso(fecha_fin):
                ple_item_estado_8 = u'8'
            ple_item_vals = {
                'periodo_1': periodo,
                'codigo_cuenta_2': line['codigo'],
                'codigo_ef_3': diario.bank_account_id.bank_id.entidad_financiera_id.num_order if diario.bank_account_id else '99',  # implementar
                'numero_doc_ef_4': diario.bank_account_id.acc_number if diario.bank_account_id else '-',
                'codigo_moneda_5': 'PEN',
                'mov_debe_6': line['debit'] if line['debit'] else '0.00',
                'mov_haber_7':line['credit'] if line['credit'] else '0.00',
                'estado_8': ple_item_estado_8,
                'company_id': company_id.id
            }
            ple_item = ple_ef.create(ple_item_vals)
            # despues de proceso
            ple_items = ple_items + ple_item.get_ple_line()
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, ple_32_old,ple_32_update, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        for line in ple_32_old:
            ple_item = self.env['account.ple.3.2'].search([
                ('codigo_cuenta_2', '=', line['codigo'])
            ], limit=1)
            ple_items = ple_items + ple_item.get_ple_line()

        for line in ple_32_update:
            ple_item = self.env['account.ple.3.2'].search([
                ('codigo_cuenta_2', '=', line['codigo'])
            ], limit=1)
            estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'

            ple_item_vals = {
                'mov_debe_6': str(line['debit']) if line['debit'] > 0 else '0.00',
                'mov_haber_7': str(line['credit']) if line['credit'] > 0 else '0.00',
                'estado_8': estado_ple,
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

    def get_32_lines(self, bc_lines):
        lines_cuenta_10 = []
        pattern = re.compile("^10")
        for line in bc_lines:
            if pattern.match(line['codigo']):
                lines_cuenta_10.append(line)
        return lines_cuenta_10

    def get_fecha_atraso(self, fecha_fin):
        grupo_libro = self.env['biosis_cont_report.grupolibroelectronico'].search([
            ('code', '=', '3')
        ], limit=1)
        if grupo_libro.type_time == 'MES':
            fecha_maxima = fecha_fin + relativedelta(months=int(grupo_libro.quantity))
        else:
            fecha_maxima = fecha_fin + relativedelta(days=int(grupo_libro.quantity))
        return fecha_maxima


