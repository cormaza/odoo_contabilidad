# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_1_2(models.Model):
    _name = 'account.ple.1.2'
    _description = u'PLE para DETALLE DE LOS MOVIMIENTOS DE LA CUENTA CORRIENTE'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable', required=True)
    codigo_ef_4 = fields.Char(string=u'Código de la entidad financiera', required=True)
    codigo_cb_contri_5 = fields.Char(string=u'Código Cuenta Bancaria del Contribuyente')
    fecha_o_6 = fields.Char(string=u'Fecha de la Operación', required=True)
    medio_pago_7 = fields.Char(string=u'Medio de pago utilizado en la operación bancaria')
    descripcion_o_b_8 = fields.Char(string=u'Descripción de la operación bancaria')
    tipo_doc_gb_9 = fields.Char(string=u'Tipo documento Girador o Beneficiario', default=u'')
    numero_doc_gb_10 = fields.Char(string=u'Número documento Girador o Beneficiario', default=u'')
    ap_d_rz_gb_11 = fields.Char(string=u'Nombre, Razon Social del Girador o Beneficiario', default=u'')
    nro_transc_bancaria_12 = fields.Char(string=u'Número de transacción bancaria, número de documento sustentatorio '
                                                u'o número de control interno de la operación bancaria', default=u'')
    mov_debe_13 = fields.Char(string=u'Movimiento del Debe', required=True)
    mov_haber_14 = fields.Char(string=u'Movimiento del Haber', required=True)
    estado_15 = fields.Char(string=u'Estado', required=True)
    move_id = fields.Many2one('account.move', string=u'Asiento Contable')
    move_line_id = fields.Many2one('account.move.line', string=u'Apunte Contable')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.cuo_2 + '|' + self.move_cuo_3 + '|' + self.codigo_ef_4 + '|' + self.codigo_cb_contri_5 + '|' \
               + self.fecha_o_6 + '|' + self.medio_pago_7 + '|' + self.descripcion_o_b_8 + '|' + self.tipo_doc_gb_9 + '|' \
               + self.numero_doc_gb_10 + '|' + self.ap_d_rz_gb_11 + '|' + self.nro_transc_bancaria_12 + '|' + self.mov_debe_13 + '|' \
               + self.mov_haber_14 + '|' + self.estado_15 + '|' + '\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_mc_res = ''
        mc_ple_list = []
        move_line_new = []
        move_new = []
        move_line_update = []
        move_update = []
        move_line = self.env['account.move.line'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('account_id.code', '=like', '104%'),
            #('account_id.code', 'not like', '104%'),
            ('company_id', '=', company_id.id),
            ('move_id.state', '!=', 'draft'),
        ]).sorted(key=lambda r: int(r.account_id.code))

        mc_ple_list = self.env['account.ple.1.2'].search([
            ('periodo_1', '=', fecha_reporte),
            ('company_id', '=', company_id.id)
        ])

        ### USANDO MOVES
        """
        move_list = []
        for move in move_line:
            if move not in move_list:
                move_list.append(move)

        move_list_mc = [line.move_id for line in mc_ple_list]

        if len(mc_ple_list) > 0:
            for move in move_list:
                if not (move in move_list_mc):
                    move_new.append(move)
                else:
                    move_update.append(move)
        else:
            move_new = move_list
            
        if len(move_new) == 0 and len(move_update) == 0:
            # warning = {
            #    'title': _('Alerta!'),
            #    'message': _('No hay movimientos para el periodo/rango seleccionado!'),
            # }
            return ' '
        else:
            if len(move_new) > 0:
                ple_nuevos = self.create_ple_items(company_id, move_new, fecha_reporte, fecha_inicio, fecha_fin)
                ple_mc_res = ple_mc_res + ple_nuevos

            if len(move_update) > 0:
                ple_modificados = self.update_ple_items(company_id, move_update, fecha_reporte, fecha_inicio, fecha_fin)
                ple_mc_res = ple_mc_res + ple_modificados

            return ple_mc_res
        """
        ###
        move_lines_mc = [line.move_line_id for line in mc_ple_list]

        if len(mc_ple_list) > 0:
            for line_ml in move_line:
                if not (line_ml in move_lines_mc):
                    move_line_new.append(line_ml)
                else:
                    move_line_update.append(line_ml)
        else:
            move_line_new = move_line

        if len(move_line_new) == 0 and len(move_line_update) == 0:
            # warning = {
            #    'title': _('Alerta!'),
            #    'message': _('No hay movimientos para el periodo/rango seleccionado!'),
            # }
            return ' '
        else:
            if len(move_line_new) > 0:
                ple_nuevos = self.create_ple_items(company_id, move_line_new, fecha_reporte, fecha_inicio, fecha_fin)
                ple_mc_res = ple_mc_res + ple_nuevos

            if len(move_line_update) > 0:
                ple_modificados = self.update_ple_items(company_id, move_line_update, fecha_reporte, fecha_inicio, fecha_fin)
                ple_mc_res = ple_mc_res + ple_modificados

            return ple_mc_res

    @api.multi
    def create_ple_items(self, company_id, move_line_new, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_mc = self.env['account.ple.1.2']
        i = 1
        for line in move_line_new:
            if datetime.date.today() <= self.get_fecha_atraso(fecha_fin):
                ple_item_estado_15 = u'1'
            elif datetime.date.today() > self.get_fecha_atraso(fecha_fin):
                ple_item_estado_15 = u'8'

            nro_cuenta = self.env['res.partner.bank'].search([
                ('partner_id','=',line.payment_id.partner_id.id),
                ('bank_id','=',line.payment_id.destination_journal_id.bank_id.id)
            ], limit=1)
            ple_item_vals = {
                'periodo_1': fecha_reporte,
                'cuo_2': line.move_id.cuo,
                'move_cuo_3': line.numero_asiento if line.numero_asiento else 'M' + str(i),
                'codigo_ef_4': line.payment_id.destination_journal_id.bank_id.entidad_financiera_id.num_order if line.payment_id.destination_journal_id.bank_id else '00',#line.move_id.payment_id.tipo_documento_pago_id.num_order,
                'codigo_cb_contri_5': nro_cuenta.acc_number if nro_cuenta else '',
                'fecha_o_6': datetime.datetime.strptime(line.date_maturity, '%Y-%m-%d').strftime('%d/%m/%Y'),  # SE APLICARA CUANDO ESTE COMPLETADO CENTRO DE COSTOS
                'medio_pago_7': line.payment_id.tipo_documento_pago_id.num_order if line.payment_id.tipo_documento_pago_id else '',
                'descripcion_o_b_8': line.payment_id.tipo_documento_pago_id.descripcion if line.payment_id.tipo_documento_pago_id else '',
                'tipo_doc_gb_9': line.payment_id.partner_id.catalog_06_id.code if line.payment_id.partner_id else '-',
                'numero_doc_gb_10': line.payment_id.partner_id.vat if line.payment_id.partner_id else '-',
                'ap_d_rz_gb_11': line.payment_id.partner_id.name if line.payment_id.partner_id else 'varios',
                'nro_transc_bancaria_12': line.payment_id.codigo_referencia_doc if line.payment_id.codigo_referencia_doc else '',
                'mov_debe_13': str(line.credit) if line.debit == 0 else '0.00',
                'mov_haber_14': str(line.debit) if line.credit == 0 else '0.00',
                'estado_15': ple_item_estado_15,
                'move_line_id': line.id,
                'company_id': company_id.id
            }
            if not (line.numero_asiento):
                line.write({'numero_asiento': 'M' + str(i)})
            ple_item = ple_mc.create(ple_item_vals)
            ple_items = ple_items + ple_item.get_ple_line()
            i = i + 1
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, move_line_update, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        for line in move_line_update:
            ple_actual = self.env['account.ple.1.2'].search([
                ('move_line_id', '=', line.id)
            ])
            if ple_actual.create_date < line.write_date:
                """
                    Validaciones para actualizar registro ple
                    """
                nro_cuenta = self.env['res.partner.bank'].search([
                    ('partner_id', '=', line.payment_id.partner_id.id),
                    ('bank_id', '=', line.payment_id.destination_journal_id.bank_id.id)
                ], limit=1)
                flag_change_payment = False
                if ple_actual.codigo_ef_4 != line.payment_id.destination_journal_id.bank_id.entidad_financiera_id.num_order:
                    flag_change_payment = True
                if ple_actual.codigo_cb_contri_5 != nro_cuenta.acc_number:
                    flag_change_payment = True
                if ple_actual.medio_pago_7 != line.payment_id.tipo_documento_pago_id.num_order:
                    flag_change_payment = True
                if ple_actual.numero_doc_gb_10 != line.payment_id.partner_id.catalog_06_id.code:
                    flag_change_payment = True
                if ple_actual.nro_transc_bancaria_12 != line.payment_id.codigo_referencia_doc:
                    flag_change_payment = True
                if ple_actual.mov_debe_13 != (str(line.credit) if line.debit == 0 else '0.00'):
                    flag_change_payment = True
                if ple_actual.mov_haber_14 != (str(line.debit) if line.credit == 0 else '0.00'):
                    flag_change_payment = True
                # if ple_actual.codigo_moneda_24 != invoice.currency_id.name:
                #   flag_change_invoice = True

                if flag_change_payment:
                    estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'
                    ple_item_vals = {
                        'move_cuo_3': line.numero_asiento,
                        'codigo_ef_4': line.payment_id.destination_journal_id.bank_id.entidad_financiera_id.num_order if line.payment_id.destination_journal_id.bank_id else '00',#line.move_id.payment_id.tipo_documento_pago_id.num_order,
                        'codigo_cb_contri_5': nro_cuenta.acc_number if nro_cuenta else '',
                        'fecha_o_6': datetime.datetime.strptime(line.date_maturity, '%Y-%m-%d').strftime('%d/%m/%Y'),  # SE APLICARA CUANDO ESTE COMPLETADO CENTRO DE COSTOS
                        'medio_pago_7': line.payment_id.tipo_documento_pago_id.num_order if line.payment_id.tipo_documento_pago_id else '',
                        'descripcion_o_b_8': line.payment_id.tipo_documento_pago_id.descripcion if line.payment_id.tipo_documento_pago_id else '',
                        'tipo_doc_gb_9': line.payment_id.partner_id.catalog_06_id.code if line.payment_id.partner_id else '-',
                        'numero_doc_gb_10': line.payment_id.partner_id.vat if line.payment_id.partner_id else '-',
                        'ap_d_rz_gb_11': line.payment_id.partner_id.name if line.payment_id.partner_id else 'varios',
                        'nro_transc_bancaria_12': line.payment_id.codigo_referencia_doc if line.payment_id.codigo_referencia_doc else '',
                        'mov_debe_13': str(line.credit) if line.debit == 0 else '0.00',
                        'mov_haber_14': str(line.debit) if line.credit == 0 else '0.00',
                        'estado_15': estado_ple,
                        'company_id': company_id.id
                    }
                    ple_actual.write(ple_item_vals)
                    ple_items = ple_items + ple_actual.get_ple_line()
            else:
                ple_items = ple_items + ple_actual.get_ple_line()
        return ple_items

    def get_fecha_atraso(self, fecha_fin):
        grupo_libro = self.env['biosis_cont_report.grupolibroelectronico'].search([
            ('code', '=', '1')
        ], limit=1)
        if grupo_libro.type_time == 'MES':
            fecha_maxima = fecha_fin + relativedelta(months=int(grupo_libro.quantity))
        else:
            fecha_maxima = fecha_fin + relativedelta(days=int(grupo_libro.quantity))
        return fecha_maxima


