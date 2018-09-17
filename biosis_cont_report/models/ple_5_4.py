# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api

class Ple_5_4(models.Model):
    _name = 'account.ple.5.4'
    _description = 'PLE para LIBRO DIARIO DE FORMATO SIMPLIFICADO - DETALLE DEL PLAN CONTABLE UTILIZADO'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuenta_cont_2 = fields.Char(string=u'Cuenta Contable', required=True)
    descripcion_cuenta_3 = fields.Char(string=u'Descripción Cuenta Contable',required=True)
    cod_plan_cuenta_4 = fields.Char(string=u'Código de Plan de Cuentas',required=True)
    desc_plan_cuenta_5 = fields.Char(string=u'Descripción de Plan de Cuentas',required=True)
    cod_cuenta_corp_6 = fields.Char(string=u'Codigo Cuenta Corporativa',required=True)
    desc_cuenta_corp_7 = fields.Char(string=u'Descripción Cuenta Corporativa',required=True)
    estado_8 = fields.Char(string=u'Estado', required=True)
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.cuenta_cont_2 + '|' + self.descripcion_cuenta_3 + '|' + self.cod_plan_cuenta_4 + '|' + self.desc_plan_cuenta_5 + '|' \
               + self.cod_cuenta_corp_6 + '|' + self.desc_cuenta_corp_7 + '|' + self.estado_8 + '|' + '\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_diario_detalle_res = ''
        diario_detalle_list = []
        cuentas_list_move = []  # Lista cuentas de moves
        cuentas_list_dd = []  # Lista cuentas de ple diario detalle
        cuentas_list_new = []

        move_list = self.env['account.move.line'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('company_id','=', company_id.id)
        ])

        diario_detalle_list = self.env['account.ple.5.4'].search([
            ('periodo_1', '=', fecha_reporte),
            ('company_id', '=', company_id.id)
        ])

        # Lista de cuentas moves lines
        if move_list:
            for line in move_list:
                if not (line.account_id.code in cuentas_list_move):
                    cuentas_list_move.append(line.account_id.code)

        # Lista de cuentas diario detalle
        if diario_detalle_list:
            for line in diario_detalle_list:
                if not (line.cuenta_cont_2 in cuentas_list_dd):
                    cuentas_list_dd.append(line.cuenta_cont_2)

        # Verificamos si existen nuevas cuentas
        if len(cuentas_list_move) > 0 and len(cuentas_list_dd) > 0:
            for cuenta in cuentas_list_move:
                if not (cuenta in cuentas_list_dd):
                    cuentas_list_new.append(cuenta)

        if len(cuentas_list_move) > 0 and len(cuentas_list_dd) == 0:
            cuentas_list_new = cuentas_list_move

        if len(cuentas_list_new) > 0:
            """
               Pasos para agregar lineas Diario Detalle al res
            """
            ple_nuevos = self.create_ple_items(company_id, cuentas_list_new, fecha_reporte, fecha_inicio, fecha_fin)
            ple_diario_detalle_res = ple_diario_detalle_res + ple_nuevos

        if len(diario_detalle_list) > 0:
            """
               Pasos para crear lineas Diario Detalle con cuentas_list_new
            """
            ple_old = self.update_ple_items(company_id, diario_detalle_list, fecha_reporte, fecha_inicio, fecha_fin)
            ple_diario_detalle_res = ple_diario_detalle_res + ple_old

        return ple_diario_detalle_res

    @api.multi
    def create_ple_items(self, company_id, cuentas_list_new, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_diario = self.env['account.ple.5.4']
        date_now = datetime.date.today()
        for cuenta in cuentas_list_new:
            if date_now >= fecha_inicio and date_now <= fecha_fin:
                ple_item_estado_8 = u'1'
            elif date_now >= fecha_fin:
                ple_item_estado_8 = u'8'

            ple_item_vals = {
                'periodo_1': fecha_reporte,
                'cuenta_cont_2': cuenta,
                'descripcion_cuenta_3': self.env['account.account'].search([('code', '=', cuenta)], limit=1).name,
                'cod_plan_cuenta_4': u'01',
                'desc_plan_cuenta_5': u'',
                'cod_cuenta_corp_6': u'',  # Cuenta corporativa SBS
                'desc_cuenta_corp_7': u'',  # Cuenta corporativa SBS
                'estado_8': ple_item_estado_8,
                'company_id': company_id.id
            }
            ple_item = ple_diario.create(ple_item_vals)
            ple_items = ple_items + ple_item.get_ple_line()

        return ple_items

    @api.multi
    def update_ple_items(self, company_id, diario_detalle_list, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_diarios = self.env['account.ple.5.4'].search([
            ('periodo_1', '=', fecha_reporte),
            ('company_id', '=', company_id.id)
        ])

        for diario in ple_diarios:
            ple_items = ple_items + diario.get_ple_line()

        return ple_items