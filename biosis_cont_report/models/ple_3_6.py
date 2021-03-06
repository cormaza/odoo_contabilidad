# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class Ple_3_6(models.Model):
    _name = 'account.ple.3.6'
    _description = u'PLE - DETALLE DEL SALDO DE LA CUENTA 19 ESTIMACIÓN DE CUENTAS DE COBRANZA DUDOSA'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable', required=True)
    tipo_doc_deu_4 = fields.Char(string=u'Tipo documento Emisor', default=u'')
    numero_doc_deu_5 = fields.Char(string=u'Número documento Emisor', default=u'')
    razon_social_deu_6 = fields.Char(string=u'Razón Social/Nombres', default=u'')
    tipo_cpbt_7 = fields.Char(string=u'Tipo Comprobante', required=True)
    serie_cpbt_8 = fields.Char(string=u'Serie del Comprobante', default=u'-')
    numero_cpbt_9 = fields.Char(string=u'Número Comprobante', required=True)
    fecha_e_10 = fields.Char(string=u'Fecha Emisión', required=True)
    mont_cobrar_11 = fields.Char(string=u'Movimiento del Debe', required=True)
    estado_12 = fields.Char(string=u'Estado', required=True)
    move_line_id = fields.Many2one('account.move.line', string=u'Apunte Contable')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.cuo_2 + '|' + self.move_cuo_3 + '|' + self.tipo_doc_deu_4 + '|' + self.numero_doc_deu_5 + '|' \
               + self.razon_social_deu_6 + '|' + self.tipo_cpbt_7 + '|' + self.serie_cpbt_8 + '|' + self.numero_cpbt_9 + '|' \
               + self.fecha_e_10 + '|' + self.mont_cobrar_11 + '|' + self.estado_12 + '|' + '\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_res = ''
        fecha_reporte_anio = str(fecha_fin.year) + '12' + '31'
        move_line_list = []
        ple_list = []
        ple_update = []
        ple_new = []

        invoice_list = self.env['account.invoice'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('type', '=', 'out_invoice'),
            ('state', '!=', 'draft'),
            ('company_id','=',company_id.id)
        ]).sorted(key=lambda r: r.date)

        for invoice in invoice_list:
            move_lines = self.env['account.move.line'].search([
                ('date', '>=', fecha_inicio),
                ('date', '<=', fecha_fin),
                ('account_id.code', '=like', '19%'),
                ('balance','<',0),
                ('invoice_id.id', '=', invoice.id),
            ], limit=1).sorted(key=lambda r: int(r.account_id.code))
            if len(move_lines) > 0:
                for line in move_lines:
                    move_line_list.append(line)

        """
        move_line_list = self.env['account.move.line'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('account_id.code', '=like', '19%'),
            ('move_id.state', '!=', 'draft'),
        ]).sorted(key=lambda r: int(r.account_id.code))
        """

        ple_list = self.env['account.ple.3.6'].search([
            ('periodo_1', '=', fecha_reporte_anio),
            ('company_id', '=', company_id.id)
        ])

        move_line_ple = [line.move_line_id for line in ple_list]

        if len(ple_list) > 0:
            for line_ml in move_line_list:
                if not (line_ml in move_line_ple):
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
        ple_model = self.env['account.ple.3.6']
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
                'tipo_doc_deu_4': line.invoice_id.partner_id.catalog_06_id.code if line.invoice_id.partner_id else '-',
                'numero_doc_deu_5': line.invoice_id.partner_id.vat if line.invoice_id.partner_id else '-',
                'razon_social_deu_6': line.invoice_id.partner_id.registration_name if line.invoice_id.partner_id.registration_name
                else (line.invoice_id.partner_id.name if line.invoice_id.partner_id else '-'),
                'tipo_cpbt_7': line.invoice_id.tipo_comprobante_id.code if line.invoice_id else '00',
                'serie_cpbt_8': line.invoice_id.numero_comprobante.split('-')[0] if line.invoice_id else '00',
                'numero_cpbt_9': line.invoice_id.numero_comprobante.split('-')[1] if line.invoice_id else '00',
                'fecha_e_10': datetime.datetime.strptime(line.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                'mont_cobrar_11': str(self.get_saldo_account_19(line, fecha_inicio, fecha_fin)) if str(line.balance) else '0.00',
                'estado_12': ple_item_estado,
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
            ple_actual = self.env['account.ple.3.6'].search([
                ('move_line_id', '=', line.id)
            ])
            if ple_actual.create_date < line.write_date:
                """
                    Validaciones para actualizar registro ple
                    """
                flag_change = False
                if ple_actual.fecha_e_10 != datetime.datetime.strptime(line.date, '%Y-%m-%d').strftime(
                        '%d/%m/%Y'):
                    flag_change = True
                if ple_actual.tipo_doc_deu_4 != line.partner_id.catalog_06_id.code:
                    flag_change = True
                if ple_actual.numero_doc_deu_5 != line.partner_id.vat:
                    flag_change = True
                if ple_actual.tipo_cpbt_7 != (line.invoice_id.tipo_comprobante_id.code if line.invoice_id else '00'):
                    flag_change = True
                if ple_actual.serie_cpbt_8 != (line.invoice_id.numero_comprobante.split('-')[0] if line.invoice_id else '00'):
                    flag_change = True
                if ple_actual.numero_cpbt_9 != (line.invoice_id.numero_comprobante.split('-')[1] if line.invoice_id else '00'):
                    flag_change = True
                if ple_actual.mont_cobrar_11 != (str(line.balance) if line.balance == 0 else '0.00'):
                    flag_change = True

                if flag_change:
                    estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'
                    ple_item_vals = {
                        'tipo_doc_deu_4': line.partner_id.catalog_06_id.code if line.partner_id else '-',
                        'numero_doc_deu_5': line.partner_id.vat if line.partner_id else '-',
                        'razon_social_deu_6': line.partner_id.registration_name if line.partner_id.registration_name
                        else (line.partner_id.name if line.partner_id else '-'),
                        'tipo_cpbt_7': line.invoice_id.tipo_comprobante_id.code if line.invoice_id else '00',
                        'serie_cpbt_8': line.invoice_id.numero_comprobante.split('-')[0] if line.invoice_id else '00',
                        'numero_cpbt_9': line.invoice_id.numero_comprobante.split('-')[1] if line.invoice_id else '00',
                        'fecha_e_10': datetime.datetime.strptime(line.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                        'mont_cobrar_11': str(self.get_saldo_account_19(line, fecha_inicio, fecha_fin)) if str(line.balance) else '0.00',
                        'estado_12': estado_ple,
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


    def get_saldo_account_19(self,line, fecha_inicio, fecha_fin):
        """
            Se obtiene el apunte contable del asiento de provision, debe haber una validacion para solo ingresar un solo asiento.
        """
        move_line_account_19 = self.env['account.move.line'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('account_id.code', '=like', '19%'),
            ('balance', '>' ,0),
            ('invoice_id.id', '=', line.invoice_id.id),
        ]).sorted(key=lambda r: int(r.account_id.code))
        saldo_debito = 0
        saldo_credito = line.balance
        for line in move_line_account_19:
            saldo_debito += line.balance


        return saldo_debito+saldo_credito