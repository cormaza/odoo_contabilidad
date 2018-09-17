# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api


class PleVentas(models.Model):
    _name = 'account.ple.14.1'
    _description = 'PLE para Ventas'

    periodo_1 = fields.Char(string=u'Periodo',required=True)
    cuo_2 = fields.Char(string=u'Codigo Único de Operación',required=True)
    move_cuo_3 = fields.Char(string=u'CUO-Asiento Contable',required=True)
    fecha_e_4 = fields.Char(string=u'Fecha Emisión',required=True)
    fecha_v_5 = fields.Char(string=u'Fecha Vencimiento',default=u'01/01/0001')
    tipo_cpbt_6 = fields.Char(string=u'Tipo Comprobante',required=True)
    serie_cpbt_7 = fields.Char(string=u'Serie del Comprobante',default=u'-')
    numero_cpbt_8 = fields.Char(string=u'Número Comprobante',required=True)
    importe_total_diario_9 = fields.Char(string=u'Importe Total Diario',default=u'')
    tipo_doc_pro_10 = fields.Char(string=u'Tipo documento Proveedor', default=u'')
    numero_doc_pro_11 = fields.Char(string=u'Número documento Proveedor', default=u'')
    razon_social_pro_12 = fields.Char(string=u'Razón Social/Nombres', default=u'')
    valor_facturado_13 = fields.Char(string=u'Valor facturado de la exportación',default=u'0.00')
    base_adq_gravadas_14 = fields.Char(string=u'Base imponible - Operaciones Gravadas', default=u'0.00')
    descuento_base_imponible_15 = fields.Char(string=u'Descuento Base Imponible',default=u'0.00')
    monto_igv_16= fields.Char(string=u'Monto IGV', default=u'0.00')
    descuento_igv_17 = fields.Char(string=u'Base imponible - Operaciones No Gravadas', default=u'0.00')
    importe_operacion_exonerada_18 = fields.Char(string=u'Importe Operación Exonerada', default=u'0.00')
    importe_operacion_inafecta_19 = fields.Char(string=u'Importe Operación Inafecta', default=u'0.00')
    isc_20 = fields.Char(string=u'Monto ISC', default=u'0.00')
    base_adq_gravadas_arroz_pilado_21 = fields.Char(string=u'Base imponible - Operaciones Gravadas - Arroz pilado', default=u'0.00')
    impuesto_ventas_arroz_pilado_22 = fields.Char(string=u'Monto ISC', default=u'0.00')
    otros_conceptos_23 = fields.Char(string=u'Otros conceptos', default=u'0.00')
    importe_total_24 = fields.Char(string=u'Importe Total', default=u'0.00')
    codigo_moneda_25 = fields.Char(string=u'Código Moneda', default=u'PEN')
    tipo_cambio_26 = fields.Char(string=u'Tipo Cambio', default=u'0.000')
    fecha_emision_doc_mod_27 = fields.Char(string=u'Fecha Emisión',default=u'01/01/0001')
    tipo_cpbt_mod_28 = fields.Char(string=u'Tipo Comprobante Modificado',default=u'00')
    serie_cpbt_mod_29 = fields.Char(string=u'Serie del Comprobante',default=u'')
    numero_cpbt_mod_codigo_dep_aduanera_30 = fields.Char(string=u'Número Comprobante/Comprobante Aduana',default=u'0')
    identificacion_contrato_31 = fields.Char(string=u'Identificación del Contrato Operadores S.I.',default=u'')
    error_tipo1_32 = fields.Char(string=u'Error 1',default=u'')
    indicador_cpbt_33 = fields.Char(string=u'Indicador de Comprobantes de pagos cancelados',default=u'')
    estado_34 = fields.Char(string=u'Estado',required=True)
    invoice_id = fields.Many2one('account.invoice', required=True, string=u'Factura')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1+'|'+self.cuo_2+'|'+self.move_cuo_3+'|'+self.fecha_e_4+'|'+self.fecha_v_5+'|'\
               +self.tipo_cpbt_6+'|'+self.serie_cpbt_7+'|'+self.numero_cpbt_8+'|'+self.importe_total_diario_9+'|'\
               +self.tipo_doc_pro_10+'|'+self.numero_doc_pro_11+'|'+self.razon_social_pro_12+'|'+self.valor_facturado_13+'|'\
               +self.base_adq_gravadas_14+'|'+self.descuento_base_imponible_15+'|'+self.monto_igv_16+'|'+self.descuento_igv_17+'|'\
               +self.importe_operacion_exonerada_18+'|'+self.importe_operacion_inafecta_19+'|'+self.isc_20+'|'+self.base_adq_gravadas_arroz_pilado_21+'|'\
               +self.impuesto_ventas_arroz_pilado_22+'|'+self.otros_conceptos_23+'|'+self.importe_total_24+'|'+self.codigo_moneda_25+'|'\
               +self.tipo_cambio_26+'|'+self.fecha_emision_doc_mod_27+'|'+self.tipo_cpbt_mod_28+'|'+self.serie_cpbt_mod_29+'|'\
               +self.numero_cpbt_mod_codigo_dep_aduanera_30+'|'+self.identificacion_contrato_31+'|'+self.error_tipo1_32+'|'+self.indicador_cpbt_33+'|'\
               +self.estado_34+'|'+'\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_ventas_res = ''
        invoices_nuevos = self.env['account.invoice'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('type', '=', 'out_invoice'),
            ('state', '!=', 'draft'),
            ('tipo_comprobante_id.code', 'in', ['01', '03', '07', '08']),
            ('company_id', '=', company_id.id),
            ('ple_generado', '=', False)
        ]).sorted(key=lambda r: r.date_due)

        invoices_old = self.env['account.invoice'].search([
            ('date', '>=', fecha_inicio),
            ('date', '<=', fecha_fin),
            ('type', '=', 'out_invoice'),
            ('state', '!=', 'draft'),
            ('tipo_comprobante_id.code', 'in', ['01', '03', '07', '08']),
            ('company_id', '=', company_id.id),
            ('ple_generado', '=', True)
        ]).sorted(key=lambda r: r.date_due)

        if len(invoices_nuevos) == 0 and len(invoices_old) == 0:
            # warning = {
            #    'title': _('Alerta!'),
            #    'message': _('No hay movimientos para el periodo/rango seleccionado!'),
            # }
            return ' '
        else:
            if len(invoices_nuevos) > 0:
                ple_nuevos = self.create_ple_items(company_id, invoices_nuevos, fecha_reporte, fecha_inicio, fecha_fin)
                ple_ventas_res = ple_ventas_res + ple_nuevos

            if len(invoices_old) > 0:
                ple_modificados = self.update_ple_items(company_id, invoices_old, fecha_inicio, fecha_fin)
                ple_ventas_res = ple_ventas_res + ple_modificados

            return ple_ventas_res

    @api.multi
    def create_ple_items(self, company_id, invoices, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_ventas = self.env['account.ple.14.1']
        for invoice in invoices:
            print invoice.write_date
            # Buscar item ple previo
            """
            ple_item_prev = self.env['account.ple.14.1'].search([
                ('cuo_2', '=', invoice.cuo_invoice),
                ('company_id', '=' , company_id.id)
            ], limit=1)
            if ple_item_prev:
                print ple_item_prev
            """
            if datetime.datetime.strptime(invoice.date_invoice,
                                          '%Y-%m-%d').date() >= fecha_inicio and datetime.datetime.strptime(
                    invoice.date_invoice, '%Y-%m-%d').date() <= fecha_fin:
                ple_item_estado_34 = u'1'
            elif datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() <= fecha_inicio:
                ple_item_estado_34 = u'8'

            ple_item_vals = {
                'periodo_1': fecha_reporte,
                'cuo_2': invoice.cuo_invoice,
                'move_cuo_3': invoice.move_id.line_ids.sorted(key=lambda line: line.id)[0].numero_asiento,
                'fecha_e_4': datetime.datetime.strptime(invoice.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                'fecha_v_5': datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime('%d/%m/%Y') if invoice.date_due else '01/01/0001',
                'tipo_cpbt_6': invoice.tipo_comprobante_id.code,
                'serie_cpbt_7': invoice.numero_comprobante.split('-')[0],
                'numero_cpbt_8': invoice.numero_comprobante.split('-')[1],
                # ple_item.importe_total_diario_9 - no implementado
                'tipo_doc_pro_10': invoice.partner_id.catalog_06_id.code,
                'numero_doc_pro_11': invoice.partner_id.vat,
                'razon_social_pro_12': invoice.partner_id.registration_name if invoice.partner_id.registration_name else '',
                # ple_item.valor_facturado_13 - no implementado
                'base_adq_gravadas_14': str(invoice.amount_untaxed),
                # ple_item.descuento_base_imponible_15 - por revisar
                'monto_igv_16': str(invoice.amount_tax),
                # ple_item.descuento_igv_17 - por revisar
                # ple_item.importe_operacion_exonerada_18 - por consultar
                # ple_item.importe_operacion_inafecta_19 - por consultar
                # ple_item.isc_20 - por consultar
                # ple_item.base_adq_gravadas_arroz_pilado_21 - por consultar
                # ple_item.impuesto_ventas_arroz_pilado_22 - por consultar
                # ple_item.otros_conceptos_23
                'importe_total_24': str(invoice.amount_total_signed),
                'codigo_moneda_25': invoice.currency_id.name,
                'tipo_cambio_26': str(format(invoice.currency_id.rate, '.3f')),  # agregar campo a invoice str(invoice.valor_tipo_cambio)
                # 'fecha_emision_doc_mod_26': (invoice.tipo_documento.code == '07' or invoice.tipo_documento.code == '08') if invoice.invoice_id.date_due.strftime('%d/%m/%Y') else '01/01/0001',
                'fecha_emision_doc_mod_27': datetime.datetime.strptime(invoice.invoice_id.date_invoice,'%Y-%m-%d').strftime('%d/%m/%Y') if (
                    invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else '01/01/0001',
                'tipo_cpbt_mod_28': invoice.invoice_id.tipo_comprobante_id.code if (
                    invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'00',
                'serie_cpbt_mod_29': invoice.invoice_id.numero_comprobante.split('-')[0] if (
                    invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'-',
                # ple_item.codigo_dep_aduanera_29
                'numero_cpbt_mod_codigo_dep_aduanera_30': invoice.invoice_id.numero_comprobante.split('-')[1] if (
                    invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'-',
                # ple_item.identificacion_contrato_31
                # ple_item.error_tipo1_32
                # ple_item.indicador_cpbt_33
                'estado_34': ple_item_estado_34,
                'invoice_id': invoice.id,
                'company_id': company_id.id
            }
            ple_item = ple_ventas.create(ple_item_vals)
            invoice.write({'ple_generado': True})
            # despues de proceso
            ple_items = ple_items + ple_item.get_ple_line()
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, invoices, fecha_inicio, fecha_fin):
        ple_items = ''
        for invoice in invoices:
            ple_actual = self.env['account.ple.14.1'].search([
                ('cuo_2', '=', invoice.cuo_invoice),
                ('company_id','=',company_id.id)
            ], limit=1)

            if ple_actual.write_date < invoice.write_date:

                if invoice.state == 'cancel':
                    ple_item_estado_34 = u'2'
                else:
                    ple_item_estado_34 = u'9'

                ple_item_vals = {
                    'periodo_1': ple_actual.periodo_1,
                    'cuo_2': invoice.cuo_invoice,
                    'move_cuo_3': invoice.move_id.line_ids.sorted(key=lambda line: line.id)[0].numero_asiento,
                    'fecha_e_4': datetime.datetime.strptime(invoice.date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                    'fecha_v_5': datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime(
                        '%d/%m/%Y') if invoice.date_due else '01/01/0001',
                    'tipo_cpbt_6': invoice.tipo_comprobante_id.code,
                    'serie_cpbt_7': invoice.numero_comprobante.split('-')[0],
                    'numero_cpbt_8': invoice.numero_comprobante.split('-')[1],
                    # ple_item.importe_total_diario_9 - no implementado
                    'tipo_doc_pro_10': invoice.partner_id.catalog_06_id.code,
                    'numero_doc_pro_11': invoice.partner_id.vat,
                    'razon_social_pro_12': invoice.partner_id.registration_name if invoice.partner_id.registration_name else '',
                    # ple_item.valor_facturado_13 - no implementado
                    'base_adq_gravadas_14': str(invoice.amount_untaxed),
                    # ple_item.descuento_base_imponible_15 - por revisar
                    'monto_igv_1_16': str(invoice.amount_tax),
                    # ple_item.descuento_igv_17 - por revisar
                    # ple_item.importe_operacion_exonerada_18 - por consultar
                    # ple_item.importe_operacion_inafecta_19 - por consultar
                    # ple_item.isc_20 - por consultar
                    # ple_item.base_adq_gravadas_arroz_pilado_21 - por consultar
                    # ple_item.impuesto_ventas_arroz_pilado_22 - por consultar
                    # ple_item.otros_conceptos_23
                    'importe_total_24': str(invoice.amount_total_signed),
                    'codigo_moneda_25': invoice.currency_id.name,
                    'tipo_cambio_26': str(format(invoice.currency_id.rate,'.3f')),
                    # 'fecha_emision_doc_mod_26': (invoice.tipo_documento.code == '07' or invoice.tipo_documento.code == '08') if invoice.invoice_id.date_due.strftime('%d/%m/%Y') else '01/01/0001',
                    'fecha_emision_doc_mod_27': datetime.datetime.strptime(invoice.invoice_id.date_invoice,
                                                                           '%Y-%m-%d').strftime('%d/%m/%Y') if (
                        invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else '01/01/0001',
                    'tipo_cpbt_mod_28': invoice.invoice_id.tipo_comprobante_id.code if (
                        invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'00',
                    'serie_cpbt_mod_29': invoice.invoice_id.numero_comprobante.split('-')[0] if (
                        invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'-',
                    # ple_item.codigo_dep_aduanera_29
                    'numero_cpbt_mod_codigo_dep_aduanera_30': invoice.invoice_id.numero_comprobante.split('-')[1] if (
                        invoice.tipo_comprobante_id.code == '07' or invoice.tipo_comprobante_id.code == '08') else u'-',
                    # ple_item.identificacion_contrato_31
                    # ple_item.error_tipo1_32
                    # ple_item.indicador_cpbt_33
                    'estado_34': ple_item_estado_34,
                    'invoice_id': invoice.id,
                    'company_id': company_id.id
                }
                ple_actual.write(ple_item_vals)
                # despues de proceso
                ple_items = ple_items + ple_actual.get_ple_line()
            else:
                ple_items = ple_items + ple_actual.get_ple_line()
        return ple_items
