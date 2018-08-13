from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EInvoiceIO(models.Model):
    _inherit = 'account.invoice'

    def envio_comprobantes(self):
        _logger.info("Tarea automatizada ")
