# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleSubscriptionCloseReasonWizard(models.TransientModel):
    _name = "sale.subscription.close.reason.wizard"

    close_reason_id = fields.Many2one("sale.subscription.close.reason", string="Close Reason", required=True)

    @api.multi
    def set_close_cancel(self):
        self.ensure_one()
        subscription = self.env['sale.subscription'].browse(self.env.context.get('active_id'))
        subscription.close_reason_id = self.close_reason_id
        if self.env.context.get('cancel'):
            subscription.set_cancel()
        else:
            subscription.set_close()
