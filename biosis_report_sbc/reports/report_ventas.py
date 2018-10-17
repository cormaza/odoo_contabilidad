# coding=utf-8

from odoo import models, fields, api, tools
import odoo.addons.decimal_precision as dp


class ReportFacturasCliente(models.Model):
    _name = 'report.ventas'
    _auto = False

    orden = fields.Char(string=u'N. ORDEN', readonly=True)
    ole_oli = fields.Char(string=u'OLE/OLI', readonly=True)
    cliente = fields.Char(string=u'CLIENTE', readonly=True)
    booking = fields.Char(string=u'BOOKING', readonly=True)
    numero_documento = fields.Char(string=u'COMPROBANTE', readonly=True)
    importe_factura = fields.Float(string=u'IMPORTE TOTAL', readonly=True)
    importe_detraccion = fields.Float(string=u'IMPORTE DETRACCION', readonly=True)
    importe_neto = fields.Float(string=u'IMPORTE NETO', readonly=True)
    fecha_emision = fields.Date(string=u'FECHA EMISION', readonly=True)
    fecha_vencimiento = fields.Date(string=u'FECHA VENCIMIENTO', readonly=True)

    def _select(self):
        return """
              inv.id, so.name as orden, (case when so.referencia_sbc is null then '-' else so.referencia_sbc end) as ole_oli,
              part.name as cliente,(case when crm.booking is null then '-' else  crm.booking end) as booking ,
              inv.number as numero_documento,
              (inv.residual_signed - inv.residual_detraccion_soles) as importe_factura,
              inv.residual_detraccion_soles as importe_detraccion, inv.residual_signed as importe_neto,
              inv.date_invoice as fecha_emision, inv.date_due as fecha_vencimiento
               """

    def _from(self):
        return """
                res_partner part inner join account_invoice inv on part.id = inv.partner_id
                inner join sale_order so on inv.origin = so.name left join
                crm_trazabilidad crm on so.id = crm.sale_order_id
                """
    def _where(self):
        return """
                inv.state='open' and inv.type = 'out_invoice'
               """

    # def _group_by(self):
    #     return """
    #           inv.id, inv.number ,inv.origin, inv.date_invoice, inv.fecha_recepcion, inv.date_due, pay.name,
    #           inv.fecha_corte, inv.fecha_pago,  inv.amount_total
    #         """

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                    SELECT
                    %s
                    FROM ( %s )
                    WHERE %s
                    )""" % (self._table, self._select(), self._from(), self._where()))


