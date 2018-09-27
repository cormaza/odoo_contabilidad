# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountMasivosDetraccion(models.Model):
    _name = 'account.masivo.detraccion'
    _description = 'Pago Masivo Detracciones'
    _rec_name = 'order_detraccion'
    _order = "id desc"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.one
    @api.depends('facturas_lineas_ids.sub_total')
    def _compute_monto_total(self):
        self.monto_total = sum((line.sub_total) for line in self.facturas_lineas_ids)

    order_detraccion= fields.Char('Nombre', required=True, index=True, copy=False, default='Nuevo')
    tipo_partner = fields.Selection([('customer', 'Cliente'), ('supplier', 'Proveedor')], required=True, default='c')
    partner_id = fields.Many2one('res.partner',string=u'Cliente/Proveedor', required=True)
    pago = fields.Many2one('account.payment', string='Pago', required=True)
    state = fields.Selection([('draft', 'Borrador'), ('open', 'Abierto'), ('reconcile', 'Conciliado')])
    monto_pago = fields.Float(string='Monto de Pago')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=_default_currency, track_visibility='always')
    monto_total = fields.Monetary(string='Total',store=True, readonly=True, compute='_compute_monto_total')
    facturas_lineas_ids = fields.One2many('account.linea.detraccion', 'detraccion_id', string='Facturas',
                                          states={'draft': [('readonly', False)]}, copy=True)

    @api.multi
    @api.onchange('tipo_partner')
    def onchange_tipo_partner(self):
        c=False
        if self.tipo_partner =='customer':
            c = True
        self.partner_id = []
        if not self.partner_id:
            return {'domain': {'partner_id': [('customer', '=', c)]}}

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        partner_id = self.partner_id
        if partner_id:
            invoices = self.env['account.invoice'].search([('partner_id', '=', partner_id.id),('pagina_detraccion', '=', True)])
            if invoices:
                pass
            else:
                raise UserError(_(
                    'Este Partner no tiene comprobantes sujetos a Detracción.'))


    @api.multi
    @api.onchange('pago')
    def onchange_pago(self):
        self.monto_pago = self.pago.amount



class AccountLineaDetraccion(models.Model):
    _name = "account.linea.detraccion"
    _description = "Invoice Line"
    _order = "detraccion_id,sequence,id"


    detraccion_id = fields.Many2one('account.masivo.detraccion', ondelete='cascade', index=True)
    partner_id = fields.Many2one('res.partner', related='detraccion_id.partner_id', string='Partner')
    factura_relacionada = fields.Many2one('account.invoice',  string='Factura relacionada')
    descripcion = fields.Char(string='Relacionado a')
    monto = fields.Float(string='Monto', required=True,digits=(5,3))
    sub_total = fields.Monetary(string='Sub Total',store=True, readonly=True, compute='_compute_monto')
    sequence = fields.Integer(default=10, help="Secuencia para la linea.")
    currency_id = fields.Many2one('res.currency', related='detraccion_id.currency_id', store=True, related_sudo=False)


    @api.one
    @api.depends('monto')
    def _compute_monto(self):
        self.sub_total = self.monto * 1

    @api.multi
    @api.onchange('factura_relacionada')
    def onchange_factura_relacionada(self):
        self.descripcion= self.factura_relacionada.partner_id.name
        self.monto = self.factura_relacionada.residual_detraccion_soles












