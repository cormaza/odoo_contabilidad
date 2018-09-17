# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    account_92_id = fields.Many2one('account.account',string=u'Cuenta destino 92')
    account_94_id = fields.Many2one('account.account',string=u'Cuenta destino 94')
    account_95_id = fields.Many2one('account.account',string=u'Cuenta destino 95')
    account_97_id = fields.Many2one('account.account',string=u'Cuenta destino 97')
    porcentaje_92 = fields.Float(string=u'Porcentaje correspondiente 92')
    porcentaje_94 = fields.Float(string=u'Porcentaje correspondiente 94')
    porcentaje_95 = fields.Float(string=u'Porcentaje correspondiente 95')
    porcentaje_97 = fields.Float(string=u'Porcentaje correspondiente 97')

    #Percepción
    percepcion = fields.Boolean(string=u'Percepción')
    monto_minimo_percepcion = fields.Float(string=u'Monto mínimo para Aplicar Percepción S/.', digits=(5,5), default=0.0)
    tipo_percepcion = fields.Many2one('account.tax', string='Tipo de Perceción')

    #Detracción
    detraccion = fields.Boolean(string=u'Detracción')
    bien_servicio = fields.Many2one('bienes.servicios.detraccion', string=u'Bien/Servicio')
    monto_minimo_detraccion = fields.Float(related='bien_servicio.monto_minimo', readonly=True,string=u'Aplicar > a', digits=(5, 2), default=0.0)
    porcentaje_detraccion = fields.Float(related='bien_servicio.porcentaje',readonly=True,string=u'Porcentaje ', digits=(3, 2), default=0.0)
    cuenta_detraccion_compra = fields.Many2one('account.account', string=u'Cuenta Detracción Compra')
    cuenta_detraccion_venta = fields.Many2one('account.account', string=u'Cuenta Detracción Venta')

    @api.multi
    @api.onchange('detraccion')
    def onchange_detraccion(self):
        self.bien_servicio = []
        self.monto_minimo_detraccion = 0
        self.porcentaje_detraccion = 0
        self.cuenta_detraccion_compra = []
        self.cuenta_detraccion_venta = []




    # centro_costos = fields.Many2one('account.centro.costos', string=u'Centro de Costos')
    #Campos auxiliares
    # @api.multi
    # @api.onchange('centro_costos')
    # def onchange_centro_costos(self):
    #     if self.centro_costos.id != False:
    #         self.vista_92 = True
    #         self.vista_94 = True
    #         self.vista_95 = True
    #         self.vista_97 = True
    #     else:
    #         self.vista_92 = False
    #         self.vista_94 = False
    #         self.vista_95 = False
    #         self.vista_97 = False

    @api.multi
    def _compute_quantities_dict(self):
        # TDE FIXME: why not using directly the function fields ?
        variants_available = self.mapped('product_variant_ids')._product_available()
        prod_available = {}
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            for p in template.product_variant_ids:
                qty_available += variants_available[p.id]["qty_available"]
                virtual_available += variants_available[p.id]["virtual_available"]
                incoming_qty += variants_available[p.id]["incoming_qty"]
                outgoing_qty += variants_available[p.id]["outgoing_qty"]
            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
            }
        return prod_available









