# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import bs4, urllib2

class NumeroComprobante(models.Model):
    _name = 'biosis.facturacion.numeracion'
    _sql_constraints = [
        ('uq_secuencia', 'unique(secuencia_id)', 'unica'),
        ('uq_secuencia_ncredito', 'unique(secuencia_ncredito_id)', 'unica'),
        ('uq_secuencia_ndebito', 'unique(secuencia_ndebito_id)', 'unica'),
    ]

    tipo_comprobante_id = fields.Many2one('einvoice.catalog.01', required=True)
    # tipo_comprobante_nombre = fields.Char(related='tipo_comprobante_id.nombre')
    # tipo_comprobante_codigo = fields.Char(related='tipo_comprobante_id.codigo')
    primera_letra = fields.Char(size=1)
    secuencia_id = fields.Many2one('ir.sequence', required=True)
    secuencia_ncredito_id = fields.Many2one('ir.sequence', required=True)
    secuencia_ndebito_id = fields.Many2one('ir.sequence', required=True)

    vigente = fields.Boolean(default=False, required=True)

    @api.model
    def create(self, vals):
        busqueda = False
        if vals['vigente']:
            busqueda = self.env['biosis.facturacion.numeracion'].search(
                ['&', ('vigente', '=', True), ('tipo_comprobante_id', '=', vals['tipo_comprobante_id'])])
        res = super(NumeroComprobante, self).create(vals)
        if busqueda:
            busqueda.write({'vigente': False})
        return res

class AccountInvoiceFact(models.Model):
    _inherit = 'account.invoice'

    numero = fields.Char(states={'draft': [('readonly', False)]})
    def obtener_numero_comprobante(self, invoice):
        tipo_comprobante = invoice.tipo_documento.code
        if invoice.tipo_documento.code in ['07', '08']:
            tipo_comprobante = invoice.invoice_id.tipo_documento.code
        obj_numeracion = self.env['biosis.facturacion.numeracion'].search(
            ['&', ('vigente', '=', True), ('tipo_comprobante_id.code', '=', tipo_comprobante)], limit=1)
        # secuencia = False
        if tipo_comprobante == '07':
            secuencia = obj_numeracion.secuencia_ncredito_id
        elif tipo_comprobante == '08':
            secuencia = obj_numeracion.secuencia_ndebito_id
        else:
            secuencia = obj_numeracion.secuencia_id
        return '%s%s' % (obj_numeracion.primera_letra, self.env['ir.sequence'].next_by_code(secuencia.code))

    @api.multi
    def invoice_validate(self):
        resultado = {'state': 'open'}
        for invoice in self:
            # refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
            # because it's probably a double encoding of the same bill/refund
            if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference),
                                ('company_id', '=', invoice.company_id.id),
                                ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
                                ('id', '!=', invoice.id)]):
                    raise UserError(_(
                        "Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))

            if invoice.type in ('out_invoice'):
                resultado['numero'] = self.obtener_numero_comprobante(invoice)

        return self.write(resultado)

    @api.multi
    def name_get(self):
        result = []
        for inv in self:
            result.append((inv.id, "%s" % inv.numero))
        return result

    #@api.multi
    #def enviar_comprobante(self, cr, uid, args):
    #    api_config = self.env['biosis.configuracion.api'].search(cr, uid, args, limit=1)
    #    return api_config

    # @api.multi
    # def seleccion_comprobante(self, invoice_id):
    #     if invoice_id:
    #         invoice = self.env['account.invoice'].search([('id', '=', invoice_id)], limit=1)
    #         if invoice:
    #             res = {'value': {}}
    #             res['value']['partner_id'] = invoice.partner_id
    #             res['value']['invoice_line_ids'] = invoice.invoice_line_ids
    #             res['value']['date_invoice'] = invoice.date_invoice
    #             return res
    #     return False

class Leyenda(models.Model):
    _name = 'biosis.facturacion.leyenda'

    codigo = fields.Char(max_length=4, string=u'Código')
    descripcion = fields.Char(u'Descripción')
    invoice_id = fields.Many2one('account.invoice')

