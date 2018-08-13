# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountNotas(models.Model):
    _name = 'account.notas'
    _inherit = 'account.invoice'

    tipo_nota= fields.Many2one('einvoice.catalog.01', string=u'Tipo Documento', required=True)

    tipo_nota_credito = fields.Many2one('einvoice.catalog.09', string=u'Tipo Nota de Crédito')
    tipo_nota_debito = fields.Many2one('einvoice.catalog.10', string=u'Tipo Nota de Débito')

    invoice_id = fields.Many2one('account.invoice', string=u'Comprobante Relacionado')

    @api.multi
    def seleccion_comprobante(self, invoice_id):
        if invoice_id:
            invoice = self.env['account.invoice'].search([('id', '=', invoice_id)], limit=1)
            if invoice:
                res = {'value': {}}
                res['value']['partner_id'] = invoice.partner_id
                res['value']['invoice_line_ids'] = invoice.invoice_line_ids
                res['value']['date_invoice'] = invoice.date_invoice
                return res
        return False




