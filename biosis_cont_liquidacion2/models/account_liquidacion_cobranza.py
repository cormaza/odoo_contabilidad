from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    fecha_emision = fields.Date(string=u'Fecha Emision')
    emisor = fields.Char(string=u'Emisor')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_liquidacion = fields.Boolean()
    servicio_id = fields.Many2one('product.product', string=u'Servicio',
                                  ondelete='restrict', index=True)
    name_liquidacion = fields.Char(string=u'Descripcion')