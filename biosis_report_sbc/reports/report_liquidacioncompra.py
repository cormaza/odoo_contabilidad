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
    moneda = fields.Char(string=u'MONEDA', readonly=True)
    total = fields.Float(string=u'IMPORTE TOTAL', readonly=True)
    saldo = fields.Float(string=u'IMPORTE TOTAL', readonly=True)




    def _select(self):
        return """
                inv.id ,inv.number as num_documento ,(case when so.referencia_sbc is null then '-' else  so.referencia_sbc end) as ole_oli,
                inv.date_invoice as fecha_factura, inv.date_due as fecha_venc,
                (case when inv.fecha_recepcion is null then inv.date_invoice else  inv.fecha_recepcion end) as fecha_recepcion,
                 pay.name as plazo_pago,inv.residual as saldo,
                inv.fecha_corte as fecha_corte,inv.fecha_pago as fecha_pago, money.symbol as moneda, inv.amount_total as total
                """

    def _from(self):
        return """
                account_invoice inv left join account_payment_term pay on inv.payment_term_id = pay.id left join sale_order so
                on inv.origin = so.name left join res_currency as money on inv.currency_id = money.id
                """
    def _where(self):
        return """
                inv.reference is NULL and inv.type = 'in_invoice' and inv.state = 'open'
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


