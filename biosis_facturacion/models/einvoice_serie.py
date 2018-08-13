# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EInvoiceSerie(models.Model):
    _name = 'biosis.facturacion.einvoice.serie'

    tipo_comprobante_id = fields.Many2one('einvoice.catalog.01', required=True, string='Tipo de comprobante')
    correlativo_id = fields.Many2one('ir.sequence', required=True, string='Correlativo')
    alfanumerico = fields.Char('Alfanumerico', required=True, size=4)
    activo = fields.Boolean('Activo', required=True, default=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Serie relacionado con una compañia")

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s" % (record.alfanumerico)))
        return result
