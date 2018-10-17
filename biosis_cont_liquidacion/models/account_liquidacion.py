# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
import calendar
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError



class AccountLiquidacion(models.Model):
    _inherit = 'account.invoice'
    _description = u'Liquidación'

    is_liquidacion = fields.Boolean()
    servicio_id = fields.Many2one('product.product', string=u'Servicio',
                                  ondelete='restrict', index=True)
    name_liquidacion = fields.Char(string=u'Descripción')
    order_liquidacion = fields.Char('Nombre', required=True, index=True, copy=False, default='Nuevo')
    numero_facturas = fields.Integer(string=u'Núm.Fact.Relacionadas')
    saldo = fields.Monetary(string=u'Monto a cuadrar')

    @api.multi
    @api.onchange('servicio_id', 'company_id')
    def onchange_proveedor_id(self):
        if self.is_liquidacion == True:
            diario = self.env['account.journal'].search([('code', '=', 'LIQ'), ('company_id', '=', self.company_id.id)],
                                                        limit=1)
            self.journal_id = {}
            self.journal_id = diario
            self.name_liquidacion = self.servicio_id.name

    @api.onchange('date_due')
    def _onchange_date_due_invoice(self):
        if self.type == 'in_invoice':
            relacion = [{'dia': 0, 'sumar': 9},
                        {'dia': 1, 'sumar': 8},
                        {'dia': 2, 'sumar': 7},
                        {'dia': 3, 'sumar': 6},
                        {'dia': 4, 'sumar': 5},
                        {'dia': 5, 'sumar': 4},
                        {'dia': 6, 'sumar': 10}]
            if self.date_due != False:
                fecha_v = datetime.strptime(self.date_due, '%Y-%m-%d')
                dia_semana_fecha_v = fecha_v.weekday()
                for rel in relacion:
                    if rel['dia'] == dia_semana_fecha_v:
                        dias = rel['sumar']
                        break
                fecha_corte = fecha_v + timedelta(days=dias)
                fecha_programada = fecha_corte + timedelta(days=5)
                self.fecha_corte = fecha_corte
                self.fecha_pago = fecha_programada
                a=1


    @api.multi
    def action_invoice_proveedor(self):
        #self.ensure_one()
        if self.saldo != self.amount_total:
            raise UserError(_("El saldo debe coincidir con el monto de la liquidación"))
        cont = 0
        for linea in self.invoice_line_ids:
            if linea:
                cont += 1

        if cont != self.numero_facturas:
            raise UserError(_("El número de facturas en linea difiere del campo Num.Fact.Relacionadas !"))

        if self.order_liquidacion == 'Nuevo':
            secuencia = self.env['ir.sequence'].next_by_code('liquidacion.compra') or '/'

        self.order_liquidacion = secuencia
        self.write({'state': 'open'})
        self.number = secuencia
        self.residual = self.saldo
        for linea in self.invoice_line_ids:
            if linea:
                linea.factura_relacionada.reference = self.order_liquidacion



    @api.multi
    def action_invoice_paid(self):
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
            raise UserError(_('Invoice must be validated in order to set it to register payment.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            raise UserError(_(
                'You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
        if self.is_liquidacion == False:
            return to_pay_invoices.write({'state': 'paid'})









            # def action_invoice_proveedor(self):
            #
            #     self.state = 'open'
            #     comprobante_id = self.env['einvoice.catalog.01'].search([('code', '=', '01')]).id
            #
            #     if self.order_liquidacion == 'New':
            #         anio = datetime.now().year
            #         secuencia = self.env['ir.sequence'].next_by_code('liquidacion.compra') or '/'
            #     liquidacion_vals = {
            #         'type': 'in_invoice',
            #         'date_invoice': datetime.now().strftime('%Y-%m-%d'),
            #         'account_id': self.account_id.id,
            #         'tipo_operacion': self.tipo_operacion,
            #         'partner_id': self.partner_id.id,
            #         'tipo_comprobante_id': comprobante_id,
            #         'state': 'draft',
            #         'currency_id': self.currency_id.id,
            #         'currency_id_soles': self.currency_id.id,
            #         'is_boleta': False,
            #         'is_liquidacion': False
            #     }
            #
            #     invoice_liquidacion = self.env['account.invoice'].create(liquidacion_vals)
            #
            #     # Crear invoice_line
            #     detalle = {
            #         'product_id': self.servicio_id.id,
            #         'price_unit': self.amount_total,
            #         'invoice_id': invoice_liquidacion.id,
            #     }
            #     line = self.env['account.invoice.line'].new(detalle)
            #     line._onchange_product_id()
            #     detalle = line._convert_to_write({name: line[name] for name in line._cache})
            #     detalle['price_unit'] = self.amount_total
            #     invoice_liquidacion.write({'invoice_line_ids': [(0, 0, detalle)]})
            #     invoice_liquidacion.compute_taxes()
            #
            #     self.order_liquidacion = secuencia
            #
            #     invoice_liquidacion.origin = secuencia
            #     return True
