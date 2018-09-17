# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api

class Ple_8_2(models.Model):
    _name = 'account.ple.8.2'
    _description = u'PLE - REGISTRO DE COMPRAS - INFORMACIÓN DE OPERACIONES CON SUJETOS NO DOMICILIADOS'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación', required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable', required=True)
    fecha_e_4 = fields.Char(string=u'Fecha Emisión', required=True)
    tipo_cpbt_5 = fields.Char(string=u'Tipo Comprobante', required=True)
    serie_cpbt_6 = fields.Char(string=u'Serie del Comprobante', default=u'-')
    numero_cpbt_7 = fields.Char(string=u'Número Comprobante', required=True)
    valor_adq_8 = fields.Char(string=u'Valor de las adquisiciones', default=u'')
    otros_conceptos_adi_9 = fields.Char(string=u'Otros conceptos adicionales', default=u'')
    importe_total_adq_10 = fields.Char(string=u'Importe total de las adquisiciones registradas', default=u'')
    tipo_cpbt_cf_11 = fields.Char(string=u'Tipo de Comprobante de Pago o Documento que sustenta el crédito fiscal', default=u'')
    serie_cpbt_cf_12 = fields.Char(string=u'Serie del comprobante de pago o documento que sustenta el crédito fiscal', default=u'')
    anio_emision_dua_dsi_13 = fields.Char(string=u'Año de Emisión DUA/DSI', default=u'0')
    numero_cpbt_cf_14 = fields.Char(string=u'Número Comprobante de pago o documento que sustenta el crédito fiscal', required=True)
    monto_igv_1_15 = fields.Char(string=u'Monto IGV 1', default=u'0.00')
    codigo_moneda_16 = fields.Char(string=u'Código Moneda', default=u'PEN')
    tipo_cambio_17 = fields.Char(string=u'Tipo Cambio', default=u'1.000')
    pais_residencia_nodo_18 = fields.Char(string=u'Pais de la residencia del sujeto no domiciliado', default=u'9589')
    razon_social_nodo_19 = fields.Char(string=u'Apellidos y nombres, denominación o razón social  del sujeto no domiciliado.', default=u'')
    domicilio_nodo_20 = fields.Char(string=u'Domicilio en el extranjero del sujeto no domiciliado', default=u'')
    nro_ident_nodo_21 = fields.Char(string=u'Número de identificación del sujeto no domiciliado', default=u'')
    nro_bene_22 = fields.Char(string=u'Número de identificación fiscal del beneficiario efectivo de los pagos', default=u'')
    razon_social_bene_23 = fields.Char(string=u'Apellidos y nombres, denominación o razón social  del beneficiario efectivo de los pagos', default=u'')
    pais_residencia_bene_24 = fields.Char(string=u'Pais de la residencia del beneficiario efectivo de los pagos', default=u'9589')
    vinculo_contr_resid_25 = fields.Char(string=u'Vínculo entre el contribuyente y el residente en el extranjero', default=u'')
    renta_bruta_26 = fields.Char(string=u'Base imponible - Operaciones Gravadas', default=u'0.00')
    renta_neta_28 = fields.Char(string=u'Base imponible - Operaciones Gravadas', default=u'0.00')
    deduccion_costo_ena_27 = fields.Char(string=u'Deducción / Costo de Enajenación de bienes de capital', default=u'0.00')
    tasa_retencion_29 = fields.Char(string=u'Tasa de retención', default=u'0.00')
    impuesto_retenido_30 = fields.Char(string=u'Impuesto retenido', default=u'0.00')
    convenios_doble_trib_31 = fields.Char(string=u'Convenios para evitar la doble imposición', default=u'')
    exoneracion_aplicada_32 = fields.Char(string=u'Exoneración aplicada', default=u'')
    tipo_renta_33 = fields.Char(string=u'Tipo de Renta', default=u'')
    mod_serv_34 = fields.Char(string=u'Modalidad del servicio prestado por el no domiciliado ', default=u'')
    aplicacion_art_76_35 = fields.Char(string=u'Aplicación del penultimo parrafo del Art. 76° de la Ley del Impuesto a la Renta', default=u'0.00')
    estado_36 = fields.Char(string=u'Estado', required=True)
    invoice_id = fields.Many2one('account.invoice', required=True, string=u'Factura')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        pass

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_compras_res = ''
        # ED sin ple
        invoices_nuevos = self.env['account.invoice'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('type', '=', 'in_invoice'),
            ('state', '!=', 'draft'),
            ('tipo_comprobante_id.code', 'in', ['00', '91', '97', '98']),
            ('company_id', '=', company_id.id),
            ('ple_generado', '=', False)
        ]).sorted(key=lambda r: r.date)

        invoices_old = self.env['account.invoice'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('type', '=', 'in_invoice'),
            ('state', '!=', 'draft'),
            ('tipo_comprobante_id.code', 'in', ['00', '91', '97', '98']),
            ('company_id', '=', company_id.id),
            ('ple_generado', '=', True)
        ]).sorted(key=lambda r: r.date)

        if len(invoices_nuevos) == 0 and len(invoices_old) == 0:
            return ' '
        else:
            if len(invoices_nuevos) > 0:
                ple_nuevos = self.create_ple_items(company_id, invoices_nuevos, fecha_reporte, fecha_inicio,
                                                           fecha_fin)
                ple_compras_res = ple_compras_res + ple_nuevos

            if len(invoices_old) > 0:
                ple_modificados = self.update_ple_items(company_id, invoices_old, fecha_fin)
                ple_compras_res = ple_compras_res + ple_modificados

        return ple_compras_res

    @api.multi
    def create_ple_items(self, company_id, invoices, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_compras = self.env['account.ple.8.2']
        # Obtener fecha limite de entrega de libro contable en caso de compras y ventas
        fechas_atraso_cv = self.env['biosis_cont_report.fechasatraso'].search([('year', '=', str(fecha_inicio.year))],
                                                                              limit=1)

        for invoice in invoices:
            # Buscar item ple previo
            # ple_item_prev = self.env['account.ple.8.1'].search([
            #    ('cuo_2', '=', invoice.cuo_invoice)
            # ], limit=1)
            # if ple_item_prev:
            #    print ple_item_prev

            if datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() >= fecha_inicio \
                    and datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() <= fecha_fin \
                    and datetime.date.today().strftime('%Y-%m-%d') <= self.get_mount_period(fecha_inicio,
                                                                                            fechas_atraso_cv):
                ple_item_estado_41 = u'1'
            elif datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() >= fecha_inicio \
                    and datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() <= fecha_fin \
                    and datetime.date.today().strftime('%Y-%m-%d') > self.get_mount_period(fecha_inicio,
                                                                                           fechas_atraso_cv):
                ple_item_estado_41 = u'6'

            ple_item_vals = {
                'periodo_1': fecha_reporte,
                'cuo_2': invoice.cuo_invoice,
                'move_cuo_3':  invoice.move_id.line_ids.sorted(key=lambda line: line.id)[0].numero_asiento,
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
                'tipo_cambio_25': str(format(invoice.currency_id.rate,'.3f')),  # agregar campo a invoice str(invoice.valor_tipo_cambio)
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
                'numero_cdd_32': invoice.numero_detraccion if invoice.numero_detraccion else u'0',
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
            ple_actual = self.env['account.ple.8.2'].search([
                ('cuo_2', '=', invoice.cuo_invoice),
                ('company_id', '=', company_id.id)
            ], limit=1)

            if ple_actual.create_date < invoice.write_date:

                """
                Validaciones para actualizar registro ple
                """
                flag_change_invoice = False
                if ple_actual.fecha_e_4 != datetime.datetime.strptime(invoice.date, '%Y-%m-%d').strftime('%d/%m/%Y'):
                    flag_change_invoice = True
                if ple_actual.fecha_v_5 != datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime(
                        '%d/%m/%Y') and ple_actual.fecha_v_5 != '01/01/0001':
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
                    if ple_actual.serie_cpbt_mod_28 != invoice.invoice_id.numero_comprobante.split('-')[
                        0] and ple_actual.serie_cpbt_mod_28 != u'-':
                        flag_change_invoice = True
                if ple_actual.numero_cdd_32 != invoice.numero_detraccion:
                    flag_change_invoice = True

                if flag_change_invoice:
                    estado_41 = u'1' if datetime.date.today() <= fecha_fin else u'9'
                    ple_item_vals = {
                        'periodo_1': ple_actual.periodo_1,
                        'cuo_2': invoice.cuo_invoice,
                        'move_cuo_3':  invoice.move_id.line_ids.sorted(key=lambda line: line.id)[0].numero_asiento,
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
                        'tipo_cambio_25': str(format(invoice.currency_id.rate,'.3f')), # agregar campo a invoice str(invoice.valor_tipo_cambio)
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