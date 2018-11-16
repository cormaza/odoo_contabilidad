# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# clase pago
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # nro correlativo
    num_letra = fields.Many2one('biosis_letras.registrarletra', string= u'Nro de letra')
    # nrocorrelativo = fields.Char(string = u'Nro Correlativo de letra',related='num_letra.nrocorrelativo')
    nrocorrelativo = fields.Char(string = u'Nro Correlativo de letra')
    monto_letra = fields.Float(strin='Monto Letra')

    @api.model
    def default_get(self, fields):
        id_factura = 0
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            id_factura = invoice['id']
            rec['communication'] = invoice['reference'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['residual']
            rec['residual_detraccion'] = invoice['residual_detraccion_soles']
            if invoice['pagina_detraccion'] == True:
                if invoice['residual_detraccion_soles'] == 0:
                    rec['pago_detraccion'] = True
                    rec['contro_detraccion'] = 0

        config_det = self.env['account.config.settings'].search(
            [('company_id', '=', self.company_id.id)], order='id desc', limit=1)
        if config_det.detraccion == 'DO':  # Una sola cuenta detraccion
            rec['journal_id'] = config_det.diario_detraccion

        factura = self.env['account.invoice'].search([('id', '=', id_factura)], limit=1)
        bandera = 0
        if factura.invoice_line_ids:
            for line in factura.invoice_line_ids:
                if line.product_id.detraccion == True:
                    bandera = 1

        if bandera == 1:
            rec['aplica_detraccion'] = True

        return rec

    def obtener_letra(self):
        a=1
