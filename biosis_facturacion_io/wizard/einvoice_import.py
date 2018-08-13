# -*- coding: utf-8 -*-
import base64
from xlrd import open_workbook, xldate_as_tuple
from zipfile import ZipFile

from odoo import models, fields, api, _


class EInvoiceImport(models.Model):
    _name = 'einvoice.ie.import'
    fichero = fields.Binary(string='Fichero a importar', required=True)
    validar = fields.Boolean(string='Validar boletas', default=False)
    fila_inicio = fields.Integer(string='Fila de inicio', default=5, required=True)
    fila_fin = fields.Integer(string='Fila de fin', required=True)

    def validar_fichero(self, sheet, inicio, fin):
        return True

    @api.multi
    def importar(self):
        tipo_igv_obj = self.env['einvoice.catalog.07']
        invoice_obj = self.env['account.invoice']
        product_obj = self.env['product.product']
        partner_obj = self.env['res.partner']
        uom_obj = self.env['product.uom']
        account_id = self.env['account.account'].search([('code', '=', '701110')], limit=1).id

        uom_unidad = uom_obj.search([('codigo_ubl', '=', 'NIU')], limit=1).id
        uom_caja = uom_obj.search([('codigo_ubl', '=', 'BX')], limit=1).id

        for wizard in self:

            wb = open_workbook(file_contents=base64.decodestring(wizard.fichero))

            sheet_names = wb.sheet_names()

            if sheet_names:
                sheet = wb.sheet_by_name(sheet_names[0])

                # row = sheet.row(wizard.fila_inicio - 1)

                comprobantes = []
                detalles = []

                if self.validar_fichero(sheet, wizard.fila_inicio - 1, wizard.fila_fin - 1):
                    invoice_actual = None
                    for row_idx in range(wizard.fila_inicio - 1, wizard.fila_fin):

                        # row = sheet.row(row_idx)
                        ncl = sheet.row_slice(row_idx, 0, 2)
                        comprobante_detalles = sheet.row_slice(row_idx, 2, 9)

                        numero_comprobante = '-'.join((str(ncl[0].value).strip(), str((int(ncl[1].value)))))

                        dl = sheet.row_slice(row_idx, 9, 17)

                        descripcion = u''.join(str(dl[1].value)).encode('utf-8').strip()
                        cantidad = int(dl[2].value)
                        uom_id = str(dl[3].value).strip() == 'UNI' and uom_unidad or uom_caja
                        precio_unitario = float(dl[4].value)
                        codigo_igv = str(int(dl[5].value))
                        tipo_igv_id = tipo_igv_obj.search([('code', '=', codigo_igv)], limit=1).id

                        detalle = {
                            'name': descripcion.upper(),
                            # 'account_id': account.id,
                            # 'invoice_id': invoice.id,
                            'product_id': False,
                            'price_unit': precio_unitario,
                            'quantity': cantidad,
                            'tipo_igv_id': tipo_igv_id,
                            'uom_id': uom_id
                        }

                        # detalles.append(detalle)

                        if numero_comprobante in [comprobante.get('ncomprobante') for comprobante in
                                                  comprobantes]:
                            # Solo agregamos detalles
                            detalle['invoice_id'] = invoice_actual.id
                            detalle['account_id'] = account_id

                            self.env['account.invoice.line'].create(detalle)

                            # for column_idx in range(9,16):
                        else:
                            if invoice_actual:
                                if wizard.validar:
                                    invoice_actual.action_invoice_open()

                            serie_str = str(ncl[0].value).replace(' ', '')
                            serie_id = self.env['biosis.facturacion.einvoice.serie'].search(
                                [('alfanumerico', '=', serie_str)], limit=1).id

                            tipo_comprobante_codigo = '%02d' % float(str(comprobante_detalles[0].value).strip())

                            tipo_comprobante_id = self.env['einvoice.catalog.01'].search(
                                [('code', '=', tipo_comprobante_codigo)], limit=1).id
                            fecha_emision = comprobante_detalles[1].value

                            fecha_tupla = xldate_as_tuple(fecha_emision, 0)

                            fecha_str = '-'.join((str(fecha_tupla[0]), str(fecha_tupla[1]), str(fecha_tupla[2])))
                            # nro_documento = comprobante_detalles[]
                            partner = partner_obj.search(
                                [('vat', '=', '%08d' % float(str(comprobante_detalles[5].value).strip()))],
                                limit=1)

                            if not partner:
                                tipo_documento_id = self.env['einvoice.catalog.06'].search(
                                    [('code', '=', '%d' % float(str(comprobante_detalles[4].value).strip()))], limit=1)
                                nombre = u''.join(comprobante_detalles[6].value).encode('utf-8').strip().upper()
                                partner_vals = {
                                    'vat': '%08d' % float(str(comprobante_detalles[5].value).strip()),
                                    'catalog_06_id': tipo_documento_id.id,
                                    'name': nombre
                                }

                                partner = partner_obj.create(partner_vals)
                                # partner.update_document()

                            invoice_vals = {
                                'serie_id': serie_id,
                                'tipo_operacion': '1',
                                'tipo_comprobante_id': tipo_comprobante_id,
                                'partner_id': partner.id,
                                'account_id': partner.property_account_receivable_id.id,
                                'reconciled': True,
                                'date_invoice': fecha_str,
                                'tipo_igv_id': tipo_igv_id,
                                'ncomprobante': numero_comprobante
                            }

                            comprobantes.append(invoice_vals)

                            invoice_actual = self.env['account.invoice'].create(invoice_vals)

                            detalle['invoice_id'] = invoice_actual.id
                            detalle['account_id'] = account_id

                            self.env['account.invoice.line'].create(detalle)
                    warning = {
                        'title': _('¡Comprobantes creados!'),
                        'message': _('Los comprobantes han sido importados presione F5'),
                    }
                    return {'warning': warning}
                    # view_id = record_id = self.env.ref('biosis_facturacion.einvoice_tree').id
                    # search_view_id = self.env.ref('account.view_account_invoice_filter').id
                    # if wizard.validar:
                    #     return {
                    #         'name': 'Comprobantes de cliente',
                    #         'type': 'ir.actions.act_window',
                    #         'view_type': 'form',
                    #         'view_mode': 'tree,kanban,form,calendar,pivot,graph',
                    #         'target': 'current',
                    #         'res_model': 'account.invoice',
                    #         'view_id': view_id,
                    #         'domain': [('type', 'in', ['out_invoice', 'out_refund']),
                    #                    ('state', 'in', ['open', ])],
                    #         'context': {'type': 'out_invoice', 'journal_type': 'sale'},
                    #         'search_view_id': search_view_id
                    #     }
                    # else:
                    #     return {
                    #         'name': 'Comprobantes de cliente',
                    #         'type': 'ir.actions.act_window',
                    #         'view_type': 'form',
                    #         'view_mode': 'tree,kanban,form,calendar,pivot,graph',
                    #         'target': 'current',
                    #         'res_model': 'account.invoice',
                    #         'view_id': view_id,
                    #         'domain': [('type', 'in', ['out_invoice', 'out_refund']), ('state', 'in', ['draft', ])],
                    #         'context': {'type': 'out_invoice', 'journal_type': 'sale'},
                    #         'search_view_id': search_view_id
                    #     }
                else:
                    pass

    def get_invoice_line_account(self, type, product, fpos, company):
        accounts = product.get_product_accounts(fpos)
        if type in ('out_invoice', 'out_refund'):
            return accounts['income']
        return accounts['expense']
