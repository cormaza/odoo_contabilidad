# coding=utf-8

from odoo import models, fields, api, tools
import odoo.addons.decimal_precision as dp


class ReportLiquidacionCompra(models.Model):
    _name = 'report.liquidacion.compra'
    _auto = False

    num_documento = fields.Char(string=u'N. DOCUMENTO', readonly=True)
    ole_oli = fields.Char(string=u'OLE/OLI', readonly=True)
    fecha_factura = fields.Date(string=u'FECHA EMISIÓN', readonly=True)
    fecha_recepcion = fields.Date(string=u'FECHA RECEPCIÓN', readonly=True)
    fecha_venc = fields.Date(string=u'FECHA VENCIMIENTO', readonly=True)
    plazo_pago = fields.Char(string=u'DÍAS CRÉDITO', readonly=True)
    fecha_corte = fields.Date(string=u'FECHA CORTE', readonly=True)
    fecha_pago = fields.Date(string=u'FECHA DE PAGO PROGRAMADA')
    total = fields.Float(string=u'IMPORTE TOTAL', readonly=True)




    def _select(self):
        return """
                inv.id ,inv.number as num_documento ,so.referencia_sbc as ole_oli, inv.date_invoice as fecha_factura,
                inv.date_due as fecha_venc,inv.fecha_recepcion as fecha_recepcion,pay.name as plazo_pago, inv.fecha_corte,
                inv.fecha_pago, inv.amount_total
                """

    def _from(self):
        return """
                account_invoice inv left join account_payment_term pay on inv.payment_term_id = pay.id left join sale_order so
                on inv.origin = so.name
                """
    def _where(self):
        return """
                where inv.reference is NULL and inv.type = 'in_invoice'
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
                    GROUP BY
                    %s
                    )""" % (self._table, self._select(), self._from(), self._where()))
                    # )""" % (self._table, self._select(), self._from(), self._where(), self._group_by()))
