# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"
    currency_id_soles = fields.Many2one('res.currency', string="Moneda soles", domain=[('name', '=', 'PEN')], default=163)
    amount_mora = fields.Monetary(string='Mora', store=True, readonly=True,default=0.0)

    @api.multi
    def cron_mora(self):

        all_subscriptions = self.env['sale.subscription'].search([('state', '=', 'open')])

        for item in all_subscriptions:
            if item.state == 'open':
                code = item.code
                facturas = self.env['account.invoice'].search([
                    ('origin', 'ilike', code),
                    ('state', '=', 'open'),
                    ('date_invoice', '>', '2018-09-01')])

                cron = self.env['ir.cron'].search([
                    ('model', 'ilike', 'sale.subscription'),
                    ('function', 'ilike', 'cron_mora')]).nextcall

                #fecha_cron = (datetime.strptime(cron, '%Y-%m-%d %H:%M:%S')).date() - timedelta(days=1)
                fecha_cron = (datetime.strptime(cron, '%Y-%m-%d %H:%M:%S')).date()


                monto = 0
                for factura in facturas:
                    fecha = factura.date_invoice
                    #dia = fecha[8:10]
                    mes = fecha[5:7]
                    anho = fecha[0:4]
                    fecha_vencimiento = anho+'-'+mes+'-10'

                    if str(fecha_cron) > fecha_vencimiento:
                        fecha_venc = datetime.strptime(fecha_vencimiento, '%Y-%m-%d')
                        #fecha_fact = datetime.strptime(fecha, '%Y-%m-%d')
                        result = fecha_cron - fecha_venc.date()
                        dias = result.days
                        monto += (dias * 5)
                        #code = factura.origin
                        #suscripcion = self.env['sale.subscription'].search([('code', 'ilike', code), ('state', '=', 'open')])
            item.amount_mora = monto




