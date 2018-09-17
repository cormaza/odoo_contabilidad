# -*- coding: utf-8 -*-
from datetime import datetime, date
import calendar
from odoo import api, fields, models, _

class AccountLiquidacion(models.Model):
    _inherit = 'account.invoice'
    _description = u'Liquidación'

    is_liquidacion = fields.Boolean()
    servicio_id = fields.Many2one('product.product', string=u'Servicio',
                                 ondelete='restrict', index=True)
    name_liquidacion = fields.Char(string=u'Descripción')
    order_liquidacion = fields.Char('Nombre', required=True, index=True, copy=False, default='New')

    @api.multi
    @api.onchange('servicio_id', 'company_id')
    def onchange_proveedor_id(self):
        if self.is_liquidacion == True:
            diario = self.env['account.journal'].search([('code', '=', 'LIQ'), ('company_id', '=', self.company_id.id)],
                                                        limit=1)
            self.journal_id = {}
            self.journal_id = diario
            self.name_liquidacion = self.servicio_id.name

    def action_invoice_proveedor(self):

        self.state = 'open'
        comprobante_id = self.env['einvoice.catalog.01'].search([('code', '=', '01')]).id

        if self.order_liquidacion == 'New':
            anio = datetime.now().year
            secuencia = self.env['ir.sequence'].next_by_code('liquidacion.compra') or '/'
        liquidacion_vals = {
            'type': 'in_invoice',
            'date_invoice': datetime.now().strftime('%Y-%m-%d'),
            'account_id': self.account_id.id,
            'tipo_operacion': self.tipo_operacion,
            'partner_id': self.partner_id.id,
            'tipo_comprobante_id': comprobante_id,
            'state': 'draft',
            'currency_id': self.currency_id.id,
            'currency_id_soles': self.currency_id.id,
            'is_boleta': False,
            'is_liquidacion': False
        }

        invoice_liquidacion = self.env['account.invoice'].create(liquidacion_vals)

        # Crear invoice_line
        detalle = {
            'product_id': self.servicio_id.id,
            'price_unit': self.amount_total,
            'invoice_id': invoice_liquidacion.id,
        }
        line = self.env['account.invoice.line'].new(detalle)
        line._onchange_product_id()
        detalle = line._convert_to_write({name: line[name] for name in line._cache})
        detalle['price_unit'] = self.amount_total
        invoice_liquidacion.write({'invoice_line_ids': [(0, 0, detalle)]})
        invoice_liquidacion.compute_taxes()

        self.order_liquidacion = secuencia
        return True










