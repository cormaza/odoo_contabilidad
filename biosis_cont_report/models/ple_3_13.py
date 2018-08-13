# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_13(models.Model):
    _name = 'account.ple.3.13'
    _description = u'PLE - DETALLE DEL SALDO DE LA CUENTA 46 CUENTAS POR PAGAR DIVERSAS – TERCEROS Y DE LA CUENTA 47 ' \
                   u'CUENTAS POR PAGAR DIVERSAS – RELACIONADAS'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable', required=True)
    tipo_doc_ter_4 = fields.Char(string=u'Tipo de Documento de Identidad del tercero', default=u'')
    numero_doc_ter_5 = fields.Char(string=u'Número de Documento de Identidad del tercero', default=u'')
    fecha_emision_6 = fields.Char(string=u'Fecha de emisión del Comprobante de Pago', required=True)
    nombre_ter_7 = fields.Char(string=u'Apellidos y Nombres de terceros', required=True)
    cod_cuenta_c_8 = fields.Char(string=u'Código de la cuenta contable asociada a la obligación', required=True)
    monto_cuenta_9 = fields.Char(string=u'Monto de cada cuenta por pagar al proveedor', default=u'-')
    estado_10 = fields.Char(string=u'Estado', required=True)
    invoice_id = fields.Many2one('account.invoice', string=u'Documento relacionado')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.cuo_2 + '|' + self.move_cuo_3 + '|' + self.tipo_doc_ter_4 + '|' + self.numero_doc_ter_5 + '|' \
               + self.fecha_emision_6 + '|' + self.nombre_ter_7 + '|' + self.cod_cuenta_c_8 + '|' + self.monto_cuenta_9 + '|' + self.estado_10 + '|' '\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_res = ''
        fecha_reporte_anio = str(fecha_fin.year) + '12' + '31'
        invoice_list = []
        ple_list = []
        ple_update = []
        ple_new = []

        invoice_list = self.env['account.invoice'].search([
            '&',
            '|',
            ('account_id.code','=like','46%'),
            ('account_id.code', '=like', '47%'),
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('type', '=', 'in_invoice'),
            ('state', '!=', 'draft'),
            ('company_id','=',company_id.id),
            ('tipo_comprobante_id.code', 'in', ['01', '03', '07', '08']),
        ])

        ple_list = self.env['account.ple.3.13'].search([
            ('periodo_1', '=', fecha_reporte_anio),
            ('company_id', '=', company_id.id)
        ])

        invoice_ple = [line.invoice_id for line in ple_list]

        if len(ple_list) > 0:
            for line in invoice_list:
                if not (line in invoice_ple):
                    ple_new.append(line)
                else:
                    ple_update.append(line)
        else:
            ple_new = invoice_list

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
        ple_model = self.env['account.ple.3.13']
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
                'move_cuo_3': 'M' + str(i),
                'tipo_doc_ter_4': line.partner_id.catalog_06_id.code if line.partner_id else '-',
                'numero_doc_ter_5': line.partner_id.vat if line.partner_id else '-',
                'fecha_emision_6': datetime.datetime.strptime(line.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                'nombre_ter_7': line.partner_id.registration_name if line.partner_id.registration_name
                else (line.partner_id.name if line.partner_id else '-'),
                'cod_cuenta_c_8': line.account_id.code,
                'monto_cuenta_9': str(line.residual) if line.residual > 0 else '0.00',
                'estado_10': ple_item_estado,
                'invoice_id': line.id,
                'company_id': company_id.id
            }
            # if not (line.numero_asiento):
            #    line.write({'numero_asiento': 'M' + str(i)})
            ple_item = ple_model.create(ple_item_vals)
            ple_items = ple_items + ple_item.get_ple_line()
            i = i + 1
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, ple_update, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        for line in ple_update:
            ple_actual = self.env['account.ple.3.13'].search([
                ('invoice_id', '=', line.id),
                ('company_id','=', company_id.id)
            ])
            if ple_actual.create_date < line.write_date:
                """
                    Validaciones para actualizar registro ple
                    """
                flag_change = False
                if ple_actual.tipo_doc_pro_4 != line.partner_id.catalog_06_id.code:
                    flag_change = True
                if ple_actual.numero_doc_pro_5 != line.partner_id.vat:
                    flag_change = True
                if ple_actual.monto_cuenta_8 != (str(line.residual) if line.residual > 0 else '0.00'):
                    flag_change = True

                if flag_change:
                    estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'
                    ple_item_vals = {
                        'tipo_doc_ter_4': line.partner_id.catalog_06_id.code if line.partner_id else '-',
                        'numero_doc_ter_5': line.partner_id.vat if line.partner_id else '-',
                        'fecha_emision_6': datetime.datetime.strptime(line.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                        'nombre_ter_7': line.partner_id.registration_name if line.partner_id.registration_name
                        else (line.partner_id.name if line.partner_id else '-'),
                        'cod_cuenta_c_8': line.account_id.code,
                        'monto_cuenta_9': str(line.residual) if line.residual > 0 else '0.00',
                        'estado_10': estado_ple,
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

