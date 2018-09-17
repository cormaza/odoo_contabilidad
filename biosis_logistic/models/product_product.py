# coding=utf-8

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if not default:
            default = dict()
        default['default_code'] = self.default_code and '(copia) ' + self.default_code or False
        return super(ProductProduct, self).copy(default)

    _sql_constraints = [
        ('default_code_unique', 'unique (default_code)',
         '¡El código de producto ya existe!'),
    ]
