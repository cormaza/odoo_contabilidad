# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

class Ple_1_1(models.Model):
    _name = 'account.ple.1.1'
    _description = u'PLE para DETALLE DE LOS MOVIMIENTOS DEL EFECTIVO'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable', required=True)
    cuenta_cont_4 = fields.Char(string=u'Cuenta Contable', required=True)
    cunio_uea_un_up_5 = fields.Char(string=u'Codigo Unidad de Operación & Unidad Economica Adm & Unidad de Negocio', default=u'')
    ccc_cu_ci_6 = fields.Char(string=u'Código Centro de Costos & Centro Utilidades % Centro de Inversión', default=u'')
    codigo_moneda_7 = fields.Char(string=u'Código Moneda', default=u'0.000')
    tipo_cpbt_8 = fields.Char(string=u'Tipo Comprobante', required=True)
    serie_cpbt_9 = fields.Char(string=u'Serie del Comprobante', default=u'-')
    numero_cpbt_10 = fields.Char(string=u'Número Comprobante', required=True)
    fecha_c_11 = fields.Char(string=u'Fecha Contable', required=True)
    fecha_v_12 = fields.Char(string=u'Fecha Vencimiento', default=u'01/01/0001')
    fecha_e_13 = fields.Char(string=u'Fecha Emisión', required=True)
    glosa_14 = fields.Char(string=u'Descripcion de la naturaleza de la operación registrada', required=True)
    glosa_referencial_15 = fields.Char(string=u'Descripción referencial', default=u'')
    mov_debe_16 = fields.Char(string=u'Movimiento del Debe', required=True)
    mov_haber_17 = fields.Char(string=u'Movimiento del Haber', required=True)
    dato_estructurado_18 = fields.Char(string=u'Dato Estructurado')
    estado_19 = fields.Char(string=u'Estado', required=True)
    move_line_id = fields.Many2one('account.move.line', string=u'Apunte Contable')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.cuo_2 + '|' + self.move_cuo_3 + '|' + self.cuenta_cont_4 + '|' + self.cunio_uea_un_up_5 + '|' \
               + self.ccc_cu_ci_6 + '|' + self.codigo_moneda_7 + '|' + self.tipo_cpbt_8 + '|' + self.serie_cpbt_9 + '|' \
               + self.numero_cpbt_10 + '|' + self.fecha_c_11 + '|' + self.fecha_v_12 + '|' + self.fecha_e_13 + '|' \
               + self.glosa_14 + '|' + self.glosa_referencial_15 + '|' + self.mov_debe_16 + '|' + self.mov_haber_17 + '|' \
               + self.dato_estructurado_18 + '|' + self.estado_19 + '|' + '\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_mf_res = ''
        mf_ple_list = []
        move_line_new = []
        move_line_update = []
        move_line = self.env['account.move.line'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('account_id.code','=like','10%'),
            ('account_id.code','not like','104%'),
            ('company_id', '=', company_id.id),
            ('move_id.state', '!=', 'draft'),
        ]).sorted(key=lambda r: int(r.account_id.code))

        mf_ple_list = self.env['account.ple.1.1'].search([
            ('periodo_1','=',fecha_reporte),
            ('company_id', '=', company_id.id)
        ])

        move_lines_mf = [line.move_line_id for line in mf_ple_list]

        if len(mf_ple_list) > 0:
            for line_ml in move_line:
                if not (line_ml in move_lines_mf):
                    move_line_new.append(line_ml)
                else:
                    move_line_update.append(line_ml)
        else:
            move_line_new = move_line

        if len(move_line_new) == 0 and len(move_line_update) == 0:
            #warning = {
            #    'title': _('Alerta!'),
            #    'message': _('No hay movimientos para el periodo/rango seleccionado!'),
            #}
            return ' '
        else:
            if len(move_line_new) > 0:
                ple_nuevos = self.create_ple_items(company_id, move_line_new, fecha_reporte, fecha_inicio, fecha_fin)
                ple_mf_res = ple_mf_res + ple_nuevos

            if len(move_line_update) > 0:
                ple_modificados = self.update_ple_items(company_id, move_line_update, fecha_reporte, fecha_inicio, fecha_fin)
                ple_mf_res = ple_mf_res + ple_modificados

            return ple_mf_res

    @api.multi
    def create_ple_items(self, company_id, move_line_new, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_mf = self.env['account.ple.1.1']
        i = 1
        for line in move_line_new:
            if datetime.date.today() <= self.get_fecha_atraso(fecha_fin):
                ple_item_estado_19 = u'1'
            elif datetime.date.today() > self.get_fecha_atraso(fecha_fin):
                ple_item_estado_19 = u'8'
            codigo_libro = '140100' if line.invoice_id.type == 'out_invoice' else '080100'
            ple_item_vals = {
                'periodo_1': fecha_reporte,
                'cuo_2': line.move_id.cuo,
                'move_cuo_3': line.numero_asiento if line.numero_asiento else 'M' + str(i),
                'cuenta_cont_4': line.account_id.code,
                'cunio_uea_un_up_5': '2',  # SE APLICARA CUANDO ESTE COMPLETADO U.E
                'ccc_cu_ci_6': '2',  # SE APLICARA CUANDO ESTE COMPLETADO CENTRO DE COSTOS
                'codigo_moneda_7': line.move_id.currency_id.name,
                'tipo_cpbt_8': line.invoice_id.tipo_comprobante_id.code if line.invoice_id.tipo_comprobante_id.code else '00',
                'serie_cpbt_9': line.invoice_id.numero_comprobante.split('-')[0] if line.invoice_id.numero_comprobante else '-',
                'numero_cpbt_10': line.invoice_id.numero_comprobante.split('-')[1] if line.invoice_id.numero_comprobante else '-',
                'fecha_c_11': datetime.datetime.strptime(line.date_maturity, '%Y-%m-%d').strftime('%d/%m/%Y'),
                'fecha_v_12': datetime.datetime.strptime(line.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                'fecha_e_13': '01/01/0001',
                'glosa_14': line.name,  # move_line.invoice_id.name if move_line.invoice_id.name else '',
                'glosa_referencial_15': '',
                'mov_debe_16': str(line.credit) if line.debit == 0 else '0.00',
                'mov_haber_17': str(line.debit) if line.credit == 0 else '0.00',
                'dato_estructurado_18': codigo_libro + '&' + fecha_reporte + '&' + line.move_id.cuo + '&' + 'M' + str(i),
                'estado_19': ple_item_estado_19,
                'move_line_id': line.id,
                'company_id': company_id.id
            }
            ple_item = ple_mf.create(ple_item_vals)
            ple_items = ple_items + ple_item.get_ple_line()
            i = i + 1
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, move_line_update, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        for line in move_line_update:
            ple_actual = self.env['account.ple.1.1'].search([
                ('move_line_id','=',line.id)
            ])
            if ple_actual.create_date < line.write_date:
                """
                    Validaciones para actualizar registro ple
                    """
                flag_change_invoice = False
                if ple_actual.fecha_c_11 != datetime.datetime.strptime(line.date_maturity, '%Y-%m-%d').strftime('%d/%m/%Y'):
                    flag_change_invoice = True
                if ple_actual.fecha_v_12 != datetime.datetime.strptime(line.date, '%Y-%m-%d').strftime(
                        '%d/%m/%Y') and ple_actual.fecha_v_12 != '01/01/0001':
                    flag_change_invoice = True
                if ple_actual.tipo_cpbt_8 != (line.invoice_id.tipo_comprobante_id.code if line.invoice_id else '00'):
                    flag_change_invoice = True
                if ple_actual.serie_cpbt_9 != (line.invoice_id.numero_comprobante.split('-')[0] if line.invoice_id else '-'):
                    flag_change_invoice = True
                if ple_actual.numero_cpbt_10 != (line.invoice_id.numero_comprobante.split('-')[1] if line.invoice_id else '-'):
                    flag_change_invoice = True
                if ple_actual.glosa_14 != line.name:
                    flag_change_invoice = True
                if ple_actual.mov_debe_16 != (str(line.credit) if line.debit == 0 else '0.00'):
                    flag_change_invoice = True
                if ple_actual.mov_haber_17 != (str(line.debit) if line.credit == 0 else '0.00'):
                    flag_change_invoice = True
                #if ple_actual.codigo_moneda_24 != invoice.currency_id.name:
                #   flag_change_invoice = True

                if flag_change_invoice:
                    codigo_libro = '140100' if line.invoice_id.type == 'out_invoice' else '080100'
                    estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'
                    ple_item_vals = {
                        'move_cuo_3': line.numero_asiento,
                        'cuenta_cont_4': line.account_id.code,
                        'cunio_uea_un_up_5': '2',  # SE APLICARA CUANDO ESTE COMPLETADO U.E
                        'ccc_cu_ci_6': '2',  # SE APLICARA CUANDO ESTE COMPLETADO CENTRO DE COSTOS
                        'codigo_moneda_7': line.move_id.currency_id.name,
                        'tipo_cpbt_8': line.invoice_id.tipo_comprobante_id.code if line.invoice_id.tipo_comprobante_id.code else '00',
                        'serie_cpbt_9': line.invoice_id.numero_comprobante.split('-')[0] if line.invoice_id.numero_comprobante else '-',
                        'numero_cpbt_10': line.invoice_id.numero_comprobante.split('-')[1] if line.invoice_id.numero_comprobante else '-',
                        'fecha_c_11': datetime.datetime.strptime(line.date_maturity, '%Y-%m-%d').strftime('%d/%m/%Y'),
                        'fecha_v_12': datetime.datetime.strptime(line.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                        'fecha_e_13': '01/01/0001',
                        'glosa_14': line.name,  # move_line.invoice_id.name if move_line.invoice_id.name else '',
                        'glosa_referencial_15': '',
                        'mov_debe_16': str(line.credit) if line.debit == 0 else '0.00',
                        'mov_haber_17': str(line.debit) if line.credit == 0 else '0.00',
                        'dato_estructurado_18': codigo_libro + '&' + fecha_reporte + '&' + line.move_id.cuo + '&' + line.numero_asiento,
                        'estado_19': estado_ple,
                        'company_id': company_id.id
                    }
                    ple_actual.write(ple_item_vals)
                    ple_items = ple_items + ple_actual.get_ple_line()
                else:
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
