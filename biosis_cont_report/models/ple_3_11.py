# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_11(models.Model):
    _name = 'account.ple.3.11'
    _description = u'PLE - DETALLE DEL SALDO DE LA CUENTA 41 REMUNERACIONES Y PARTICIPACIONES POR PAGAR (PCGE)'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable', required=True)
    cuenta_cont_4 = fields.Char(string=u'Cuenta contable', default=u'')
    tipo_doc_tra_5 = fields.Char(string=u'Tipo documento Trabajador', default=u'')
    numero_doc_tra_6 = fields.Char(string=u'Número documento Trabajador', default=u'')
    cod_tra_7 = fields.Char(string=u'Código del trabajador', required=True)
    nombre_tra_8 = fields.Char(string=u'Apellidos y nombres del trabajador', required=True)
    saldo_final_9 = fields.Char(string=u'Saldo Final', default=u'-')
    estado_10 = fields.Char(string=u'Estado', required=True)
    move_line_id = fields.Many2one('account.move.line', string=u'Apunte Contable')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.cuo_2 + '|' + self.move_cuo_3 + '|' + self.cuenta_cont_4 + '|' + self.tipo_doc_tra_5 + '|' \
               + self.numero_doc_tra_6 + '|' + self.cod_tra_7 + '|' + self.nombre_tra_8 + '|' + self.saldo_final_9 + '|' \
               + self.estado_10 + '|' + '\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_res = ''
        fecha_reporte_anio = str(fecha_fin.year) + '12' + '31'
        move_line_list = []
        ple_list = []
        ple_update = []
        ple_new = []

        move_line_list = self.env['account.move.line'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('account_id.code', '=like', '41%'),
            ('move_id.state', '!=', 'draft'),
            ('company_id', '=', company_id.id)
        ]).sorted(key=lambda r: int(r.account_id.code))

        ple_list = self.env['account.ple.3.11'].search([
            ('periodo_1', '=', fecha_reporte_anio),
            ('company_id','=', company_id.id)
        ])

        move_lines_ple = [line.move_line_id for line in ple_list]

        if len(ple_list) > 0:
            for line_ml in move_line_list:
                if not (line_ml in move_lines_ple):
                    ple_new.append(line_ml)
                else:
                    ple_update.append(line_ml)
        else:
            ple_new = move_line_list

        if len(ple_new) == 0 and len(ple_update) == 0:
            # warning = {
            #    'title': _('Alerta!'),
            #    'message': _('No hay movimientos para el periodo/rango seleccionado!'),
            # }
            return ' '
        else:
            if len(ple_new) > 0:
                ple_nuevos = self.create_ple_items(company_id, ple_new, fecha_reporte, fecha_inicio, fecha_fin)
                ple_res = ple_res + ple_nuevos

            if len(ple_update) > 0:
                ple_modificados = self.update_ple_items(company_id, ple_update, fecha_reporte, fecha_inicio, fecha_fin)
                ple_res = ple_res + ple_modificados

            return ple_res

    @api.multi
    def create_ple_items(self, company_id, ple_new, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_model = self.env['account.ple.3.11']
        periodo = str(fecha_fin.year) + '12' + '31'
        i = 1
        for line in ple_new:
            if datetime.date.today() <= self.get_fecha_atraso(fecha_fin):
                ple_item_estado = u'1'
            elif datetime.date.today() > self.get_fecha_atraso(fecha_fin):
                ple_item_estado = u'8'
            ple_item_vals = {
                'periodo_1': periodo,
                'cuo_2': line.move_id.cuo,
                'move_cuo_3': line.numero_asiento if line.numero_asiento else 'M' + str(i),
                'cuenta_cont_4': line.account_id.code,
                'tipo_doc_tra_5': line.partner_id.catalog_06_id.code if line.partner_id else '-',
                'numero_doc_tra_6': line.partner_id.vat if line.partner_id else '-',
                'cod_tra_7': line.partner_id.vat if line.partner_id else '-',
                'nombre_tra_8': line.partner_id.name if line.partner_id else '-',
                'saldo_final_9': str(line.balance) if line.balance else '0.00',
                'estado_10': ple_item_estado,
                'move_line_id': line.id,
                'company_id': company_id.id
            }
            if not (line.numero_asiento):
                line.write({'numero_asiento': 'M' + str(i)})
            ple_item = ple_model.create(ple_item_vals)
            ple_items = ple_items + ple_item.get_ple_line()
            i = i + 1
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, ple_update, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        for line in ple_update:
            ple_actual = self.env['account.ple.3.11'].search([
                ('move_line_id', '=', line.id)
            ])
            if ple_actual.create_date < line.write_date:
                """
                    Validaciones para actualizar registro ple
                    """
                flag_change = False
                if ple_actual.cuenta_cont_4 != line.account_id.code:
                    flag_change = True
                if ple_actual.numero_doc_tra_6 != line.partner_id.vat:
                    flag_change = True
                if ple_actual.nombre_tra_8 != line.partner_id.name:
                    flag_change = True
                if ple_actual.saldo_final_9 != (str(line.balance) if line.balance else '0.00'):
                    flag_change = True

                if flag_change:
                    estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'
                    ple_item_vals = {
                        'cuenta_cont_4': line.account_id.code,
                        'tipo_doc_tra_5': line.partner_id.catalog_06_id.code if line.partner_id else '-',
                        'numero_doc_tra_6': line.partner_id.vat if line.partner_id else '-',
                        'cod_tra_7': line.partner_id.vat if line.partner_id else '-',
                        'nombre_tra_8': line.partner_id.name if line.partner_id else '-',
                        'saldo_final_9': str(line.balance) if line.balance else '0.00',
                        'estado_10': estado_ple,
                        'company_id': company_id.id
                    }
                    ple_actual.write(ple_item_vals)
                    ple_items = ple_items + ple_actual.get_ple_line()
            else:
                ple_items = ple_items + ple_actual.get_ple_line()
        return ple_items

    def get_fecha_atraso(self, fecha_fin):
        grupo_libro = self.env['biosis_cont_report.grupolibroelectronico'].search([
            ('code', '=', '3')
        ], limit=1)
        if grupo_libro.type_time == 'MES':
            fecha_maxima = fecha_fin + relativedelta(months=int(grupo_libro.quantity))
        else:
            fecha_maxima = fecha_fin + relativedelta(days=int(grupo_libro.quantity))
        return fecha_maxima