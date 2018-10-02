# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api


class Ple_8_1(models.Model):
    _name = 'account.ple.8.1'
    _description = 'PLE para Compras'

    periodo_1 = fields.Char(string=u'Periodo',required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación',required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable',required=True)
    fecha_e_4 = fields.Char(string=u'Fecha Emisión',required=True)
    fecha_v_5 = fields.Char(string=u'Fecha Vencimiento',default=u'01/01/0001')
    tipo_cpbt_6 = fields.Char(string=u'Tipo Comprobante',required=True)
    serie_cpbt_7 = fields.Char(string=u'Serie del Comprobante',default=u'-')
    anio_emision_dua_dsi_8 = fields.Char(string=u'Año de Emisión DUA/DSI',default=u'0')
    numero_cpbt_9 = fields.Char(string=u'Número Comprobante',required=True)
    importe_total_diario_10 = fields.Char(string=u'Importe Total Diario',default=u'')
    tipo_doc_pro_11 = fields.Char(string=u'Tipo documento Proveedor', default=u'')
    numero_doc_pro_12 = fields.Char(string=u'Número documento Proveedor', default=u'')
    razon_social_pro_13 = fields.Char(string=u'Razón Social/Nombres', default=u'')
    base_adq_gravadas_14 = fields.Char(string=u'Base imponible - Operaciones Gravadas', default=u'0.00')
    monto_igv_1_15= fields.Char(string=u'Monto IGV 1', default=u'0.00')
    base_adq_no_gravadas_16 = fields.Char(string=u'Base imponible - Operaciones No Gravadas', default=u'0.00')
    monto_igv_2_17 = fields.Char(string=u'Monto IGV 2', default=u'0.00')
    base_adq_sin_df_18 = fields.Char(string=u'Base imponible - Sin derecho fiscal', default=u'0.00')
    monto_igv_3_19 = fields.Char(string=u'Monto IGV 3', default=u'0.00')
    valor_adq_no_gravadas_20 = fields.Char(string=u'Valor adquisiones no gravadas', default=u'0.00')
    monto_isc_21 = fields.Char(string=u'Monto ISC', default=u'0.00')
    otros_conceptos_22 = fields.Char(string=u'Otros conceptos', default=u'0.00')
    importe_total_23 = fields.Char(string=u'Importe Total',required=True)
    codigo_moneda_24 = fields.Char(string=u'Código Moneda', default=u'PEN')
    tipo_cambio_25 = fields.Char(string=u'Tipo Cambio', default=u'1.000')
    fecha_emision_doc_mod_26 = fields.Char(string=u'Fecha Emisión',default=u'01/01/0001')
    tipo_cpbt_mod_27 = fields.Char(string=u'Tipo Comprobante Modificado',default=u'00')
    serie_cpbt_mod_28 = fields.Char(string=u'Serie del Comprobante',default=u'-')
    codigo_dep_aduanera_29 = fields.Char(string=u'Comprobante Aduana',default=u'')
    numero_cpbt_mod_30 = fields.Char(string=u'Serie del Comprobante',default=u'-')
    fecha_emision_cdd_31 = fields.Char(string=u'Fecha Emision de CDD',default=u'01/01/0001')
    numero_cdd_32 = fields.Char(string=u'Número de CDD',default=u'0')
    marca_cpbt_33 = fields.Char(string=u'Marca del comprobante de pago',default=u'')
    clasif_bienes_34 = fields.Char(string=u'Clasificación de bienes y servicios',default=u'')
    identif_contrato_s_i_35 = fields.Char(string=u'Identificación del Contrato Operadores S.I.',default=u'')
    error_tipo1_36 = fields.Char(string=u'Error 1',default=u'')
    error_tipo2_37 = fields.Char(string=u'Error 2',default=u'')
    error_tipo3_38 = fields.Char(string=u'Error 3',default=u'')
    error_tipo4_39 = fields.Char(string=u'Error 4',default=u'')
    indicador_cpbt_40 = fields.Char(string=u'Indicador de Comprobantes de pagos cancelados',default=u'')
    estado_41 = fields.Char(string=u'Estado',required=True)
    invoice_id = fields.Many2one('account.invoice', required=True, string=u'Factura')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1+'|'+self.cuo_2+'|'+self.move_cuo_3+'|'+self.fecha_e_4+'|'+self.fecha_v_5+'|'\
               +self.tipo_cpbt_6+'|'+self.serie_cpbt_7+'|'+self.anio_emision_dua_dsi_8+'|'+self.numero_cpbt_9+'|'\
               +self.importe_total_diario_10+'|'+self.tipo_doc_pro_11+'|'+self.numero_doc_pro_12+'|'+self.razon_social_pro_13+'|'\
               +self.base_adq_gravadas_14+'|'+self.monto_igv_1_15+'|'+self.base_adq_no_gravadas_16+'|'+self.monto_igv_2_17+'|'\
               +self.base_adq_sin_df_18+'|'+self.monto_igv_3_19+'|'+self.valor_adq_no_gravadas_20+'|'+self.monto_isc_21+'|'\
               +self.otros_conceptos_22+'|'+self.importe_total_23+'|'+self.codigo_moneda_24+'|'+self.tipo_cambio_25+'|'\
               +self.fecha_emision_doc_mod_26+'|'+self.tipo_cpbt_mod_27+'|'+self.serie_cpbt_mod_28+'|'+self.codigo_dep_aduanera_29+'|'\
               +self.numero_cpbt_mod_30+'|'+self.fecha_emision_cdd_31+'|'+self.numero_cdd_32+'|'+self.marca_cpbt_33+'|'\
               +self.clasif_bienes_34+'|'+self.identif_contrato_s_i_35+'|'+self.error_tipo1_36+'|'+self.error_tipo2_37+'|'\
               +self.error_tipo3_38+'|'+self.error_tipo4_39+'|'+self.indicador_cpbt_40+'|'+self.estado_41+'|'+'\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_compras_res = ''
        # ED sin ple
        invoices_nuevos = self.env['account.invoice'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('type', '=', 'in_invoice'),
            ('state', '!=', 'draft'),
            ('tipo_comprobante_id.code', 'in', ['01', '03', '07', '08']),
            ('company_id','=',company_id.id),
            ('ple_generado', '=', False)
        ]).sorted(key=lambda r: r.date)

        invoices_old = self.env['account.invoice'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('type', '=', 'in_invoice'),
            ('state', '!=', 'draft'),
            ('tipo_comprobante_id.code', 'in', ['01', '03', '07', '08']),
            ('company_id', '=', company_id.id),
            ('ple_generado', '=', True)
        ]).sorted(key=lambda r: r.date)

        if len(invoices_nuevos) == 0 and len(invoices_old) == 0:
            # warning = {
            #    'title': _('Alerta!'),
            #    'message': _('No hay movimientos para el periodo/rango seleccionado!'),
            # }
            return ' '
        else:
            if len(invoices_nuevos) > 0:
                ple_nuevos = self.create_ple_items(company_id, invoices_nuevos, fecha_reporte, fecha_inicio, fecha_fin)
                ple_compras_res = ple_compras_res + ple_nuevos

            if len(invoices_old) > 0:
                ple_modificados = self.update_ple_items(company_id, invoices_old, fecha_fin)
                ple_compras_res = ple_compras_res + ple_modificados

        return ple_compras_res

    @api.multi
    def create_ple_items(self, company_id, invoices, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_compras = self.env['account.ple.8.1']
        #Obtener fecha limite de entrega de libro contable en caso de compras y ventas
        fechas_atraso_cv = self.env['biosis_cont_report.fechasatraso'].search([('year','=',str(fecha_inicio.year))],limit=1)

        for invoice in invoices:
            # Buscar item ple previo
            #ple_item_prev = self.env['account.ple.8.1'].search([
            #    ('cuo_2', '=', invoice.cuo_invoice)
            #], limit=1)
            #if ple_item_prev:
            #    print ple_item_prev

            if datetime.datetime.strptime(invoice.date_invoice,'%Y-%m-%d').date() >= fecha_inicio \
                    and datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() <= fecha_fin \
                    and datetime.date.today().strftime('%Y-%m-%d') <= self.get_mount_period(fecha_inicio, fechas_atraso_cv):
                ple_item_estado_41 = u'1'
            elif datetime.datetime.strptime(invoice.date_invoice,'%Y-%m-%d').date() >= fecha_inicio \
                    and datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() <= fecha_fin \
                    and datetime.date.today().strftime('%Y-%m-%d') > self.get_mount_period(fecha_inicio, fechas_atraso_cv):
                ple_item_estado_41 = u'6'

            ple_item_vals = {
                'periodo_1': fecha_reporte,
                'cuo_2': invoice.cuo_invoice,
                'move_cuo_3': invoice.move_id.line_ids.sorted(key=lambda line: line.id)[0].numero_asiento,
                'fecha_e_4': datetime.datetime.strptime(invoice.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                'fecha_v_5': datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime(
                    '%d/%m/%Y') if invoice.date_due else '01/01/0001',
                'tipo_cpbt_6': invoice.tipo_comprobante_id.code,
                'serie_cpbt_7': invoice.numero_comprobante.split('-')[0],
                # ple_item.anio_emision_dua_dsi_8 -> no implementado
                'numero_cpbt_9': invoice.numero_comprobante.split('-')[1],
                # ple_item.importe_total_diario_10 - no implementado
                'tipo_doc_pro_11': invoice.partner_id.catalog_06_id.code,
                'numero_doc_pro_12': invoice.partner_id.vat,
                'razon_social_pro_13': invoice.partner_id.registration_name if invoice.partner_id.registration_name else invoice.partner_id.name,
                'base_adq_gravadas_14': str(invoice.amount_untaxed),
                'monto_igv_1_15': str(invoice.amount_tax),
                # ple_item.base_adq_no_gravadas_16 - por consultar
                # ple_item.monto_igv_2_17
                # ple_item.base_adq_sin_df_18
                # ple_item.monto_igv_3_19
                # ple_item.valor_adq_no_gravadas_20
                # ple_item.monto_isc_21
                # ple_item.otros_conceptos_22
                'importe_total_23': str(invoice.amount_total_signed),
                'codigo_moneda_24': invoice.currency_id.name,
                'tipo_cambio_25':  str(format(invoice.currency_id.rate,'.3f')),  # agregar campo a invoice str(invoice.valor_tipo_cambio)
                'fecha_emision_doc_mod_26': datetime.datetime.strptime(invoice.invoice_id.date_due,
                                                                       '%Y-%m-%d').strftime('%d/%m/%Y') if (
                    invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else '01/01/0001',
                'tipo_cpbt_mod_27': invoice.invoice_id.tipo_comprobante_id.code if (
                    invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'00',
                'serie_cpbt_mod_28': invoice.invoice_id.numero_comprobante.split('-')[0] if (
                    invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'-',
                # ple_item.codigo_dep_aduanera_29
                'numero_cpbt_mod_30': invoice.invoice_id.numero_comprobante.split('-')[1] if (
                    invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'-',
                'fecha_emision_cdd_31': datetime.datetime.strptime(invoice.fecha_emision_detraccion,
                                                                   '%Y-%m-%d').strftime(
                    '%d/%m/%Y') if invoice.fecha_emision_detraccion else u'01/01/0001',
                'numero_cdd_32': invoice.numero_detraccion if invoice.numero_detraccion else u'',
                # ple_item.marca_cpbt_33
                # ple_item.clasif_bienes_34
                # ple_item.identif_contrato_s_i_35
                # ple_item.error_tipo1_36
                # ple_item.error_tipo2_37
                # ple_item.error_tipo3_38
                # ple_item.error_tipo4_39
                # ple_item.indicador_cpbt_40
                'estado_41': ple_item_estado_41,
                'invoice_id': invoice.id,
                'company_id': company_id.id
            }
            ple_item = ple_compras.create(ple_item_vals)
            invoice.write({'ple_generado': True})
            # despues de proceso
            ple_items = ple_items + ple_item.get_ple_line()
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, invoices, fecha_fin):
        ple_items = ''
        for invoice in invoices:
            ple_actual = self.env['account.ple.8.1'].search([
                ('cuo_2', '=', invoice.cuo_invoice),
                ('company_id','=',company_id.id)
            ], limit=1)

            if ple_actual.create_date < invoice.write_date:

                """
                Validaciones para actualizar registro ple
                """
                flag_change_invoice = False
                if ple_actual.fecha_e_4 != datetime.datetime.strptime(invoice.date, '%Y-%m-%d').strftime('%d/%m/%Y'):
                    flag_change_invoice = True
                if ple_actual.fecha_v_5 != datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime('%d/%m/%Y') and ple_actual.fecha_v_5 != '01/01/0001':
                    flag_change_invoice = True
                if ple_actual.tipo_cpbt_6 != invoice.tipo_comprobante_id.code:
                    flag_change_invoice = True
                if ple_actual.serie_cpbt_7 != invoice.numero_comprobante.split('-')[0]:
                    flag_change_invoice = True
                if ple_actual.numero_cpbt_9 != invoice.numero_comprobante.split('-')[1]:
                    flag_change_invoice = True
                if ple_actual.numero_doc_pro_12 != invoice.partner_id.vat:
                    flag_change_invoice = True
                if ple_actual.base_adq_gravadas_14 != str(invoice.amount_untaxed):
                    flag_change_invoice = True
                if ple_actual.monto_igv_1_15 != str(invoice.amount_tax):
                    flag_change_invoice = True
                if ple_actual.codigo_moneda_24 != invoice.currency_id.name:
                    flag_change_invoice = True
                if invoice.invoice_id:
                    if ple_actual.serie_cpbt_mod_28 != invoice.invoice_id.numero_comprobante.split('-')[0] and ple_actual.serie_cpbt_mod_28 !=  u'-':
                        flag_change_invoice = True
                if ple_actual.numero_cdd_32 != invoice.numero_detraccion:
                    flag_change_invoice = True

                if flag_change_invoice:
                    estado_41 = u'1' if datetime.date.today() <= fecha_fin else u'9'
                    ple_item_vals = {
                        'periodo_1': ple_actual.periodo_1,
                        'cuo_2': invoice.cuo_invoice,
                        'move_cuo_3': invoice.move_id.line_ids.sorted(key=lambda line: line.id)[0].numero_asiento,
                        'fecha_e_4': datetime.datetime.strptime(invoice.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                        'fecha_v_5': datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime(
                            '%d/%m/%Y') if invoice.date_due else '01/01/0001',
                        'tipo_cpbt_6': invoice.tipo_comprobante_id.code,
                        'serie_cpbt_7': invoice.numero_comprobante.split('-')[0],
                        # ple_item.anio_emision_dua_dsi_8 -> no implementado
                        'numero_cpbt_9': invoice.numero_comprobante.split('-')[1],
                        # ple_item.importe_total_diario_10 - no implementado
                        'tipo_doc_pro_11': invoice.partner_id.catalog_06_id.code,
                        'numero_doc_pro_12': invoice.partner_id.vat,
                        'razon_social_pro_13': invoice.partner_id.registration_name,
                        'base_adq_gravadas_14': str(invoice.amount_untaxed),
                        'monto_igv_1_15': str(invoice.amount_tax),
                        # ple_item.base_adq_no_gravadas_16 - por consultar
                        # ple_item.monto_igv_2_17
                        # ple_item.base_adq_sin_df_18
                        # ple_item.monto_igv_3_19
                        # ple_item.valor_adq_no_gravadas_20
                        # ple_item.monto_isc_21
                        # ple_item.otros_conceptos_22
                        'importe_total_23': str(invoice.amount_total_signed),
                        'codigo_moneda_24': invoice.currency_id.name,
                        'tipo_cambio_25':  str(format(invoice.currency_id.rate,'.3f')),
                        # 'fecha_emision_doc_mod_26': (invoice.tipo_documento.code == '07' or invoice.tipo_documento.code == '08') if invoice.invoice_id.date_due.strftime('%d/%m/%Y') else '01/01/0001',
                        'fecha_emision_doc_mod_26': datetime.datetime.strptime(invoice.invoice_id.date_due,
                                                                               '%Y-%m-%d').strftime('%d/%m/%Y') if (
                            invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'01/01/0001',
                        'tipo_cpbt_mod_27': invoice.invoice_id.tipo_comprobante_id.code if (
                            invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'00',
                        'serie_cpbt_mod_28': invoice.invoice_id.numero_comprobante.split('-')[0] if (
                            invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'-',
                        # ple_item.codigo_dep_aduanera_29
                        'numero_cpbt_mod_30': invoice.invoice_id.numero_comprobante.split('-')[1] if (
                            invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'-',
                        'fecha_emision_cdd_31': datetime.datetime.strptime(invoice.fecha_emision_detraccion,
                                                                           '%Y-%m-%d').strftime(
                            '%d/%m/%Y') if invoice.fecha_emision_detraccion else u'01/01/0001',
                        'numero_cdd_32': invoice.numero_detraccion if invoice.numero_detraccion else u'0',
                        # ple_item.marca_cpbt_33
                        # ple_item.clasif_bienes_34
                        # ple_item.identif_contrato_s_i_35
                        # ple_item.error_tipo1_36
                        # ple_item.error_tipo2_37
                        # ple_item.error_tipo3_38
                        # ple_item.error_tipo4_39
                        # ple_item.indicador_cpbt_40
                        'estado_41': estado_41,
                        'invoice_id': invoice.id,
                        'company_id': company_id.id
                    }
                    ple_actual.write(ple_item_vals)
                    # despues de proceso
                    ple_items = ple_items + ple_actual.get_ple_line()
                else:
                    ple_items = ple_items + ple_actual.get_ple_line()
            else:
                ple_items = ple_items + ple_actual.get_ple_line()
        return ple_items


    def get_mount_period(self, fecha_inicio, fechas_atraso_cv):
        print fecha_inicio.month
        return {
            '1': fechas_atraso_cv.january,
            '2': fechas_atraso_cv.february,
            '3': fechas_atraso_cv.march,
            '4': fechas_atraso_cv.april,
            '5': fechas_atraso_cv.may,
            '6': fechas_atraso_cv.june,
            '7': fechas_atraso_cv.july,
            '8': fechas_atraso_cv.august,
            '9': fechas_atraso_cv.september,
            '10': fechas_atraso_cv.october,
            '11': fechas_atraso_cv.november,
            '12': fechas_atraso_cv.december,
        }.get(str(fecha_inicio.month))
