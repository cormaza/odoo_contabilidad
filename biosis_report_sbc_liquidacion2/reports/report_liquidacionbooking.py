# coding=utf-8

from odoo import models, fields, api, tools
import odoo.addons.decimal_precision as dp


class ReportLiquidacionbooking(models.Model):
    _name = 'report.liquidacion.booking'
    _auto = False

    orden = fields.Char(string=u'ORDEN', readonly=True)
    cliente = fields.Char(string=u'CLIENTE', readonly=True)
    booking = fields.Char(string=u'BOOKING', readonly=True)
    tipodoc = fields.Char(string=u'TIPO DOC', readonly=True)
    nrodocumento = fields.Char(string=u'NRO DOCUMENTO', readonly=True)
    importe = fields.Float(string=u'IMPORTE', readonly=True)
    det = fields.Float(string=u'DET', readonly=True)
    neto = fields.Float(string=u'NETO')
    fecemision = fields.Date(string=u'FEC. EMISIÓN', readonly=True)
    fecrecepcion = fields.Date(string=u'FEC. RECEPCIÓN')
    fecvenc = fields.Date(string=u'FEC. VENCIMIENTO', readonly=True)

    def _select(self):
        return """
                so.name as orden, part.name as cliente,(case when crm.booking is null then '-' else  crm.booking end) as booking  ,
                inv.number as numero_documento,
                (inv.residual_signed - inv.residual_detraccion_soles) as importe,
                 inv.residual_detraccion_soles as det, inv.residual_signed as neto,
                 inv.date_invoice as fecemision, inv.date_due as fecvenc
                """

    def _from(self):
        return """
             res_partner part inner join account_invoice inv on part.id = inv.partner_id
              inner join sale_order so on inv.origin = so.name left join
              crm_trazabilidad crm on so.id = crm.sale_order_id
                """
    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                    SELECT
                    %s
                    FROM ( %s )                   
                    %s
                    )""" % (self._table, self._select(), self._from()))
