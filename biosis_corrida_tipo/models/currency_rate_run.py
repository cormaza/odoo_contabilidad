from odoo import fields, models, api, tools


class CurrencyRateRun(models.Model):
    _name = 'currency.rate.run'
    _description = "Corrida de Tipo de Cambio"
    _auto = False
    # _order = 'fecha asc, comprobante asc'

    id = fields.Char()
    corrida = fields.Boolean()
    fecha = fields.Date(string=u'Fecha', readonly=True)
    comprobante = fields.Char(string=u'Comprobante', readonly=True)
    precio = fields.Float(string=u'precio', readonly=True)
    importe = fields.Float(string=u'Importe $', readonly=True)
    montofactura = fields.Float(string=u'Importe s/', readonly=True)
    cierre = fields.Float(string=u'Cierre', readonly=True)
    total = fields.Float(string=u'Total', readonly=True)
    ajuste = fields.Float(string=u'Ajuste', readonly=True)




    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                 %s
                 )""" % (self._table, self._query_view()))

    def _query_view(self):
        query = """

select
       row_number() over (order by f.id = m.id) as id,
       a.corrida as corrida,f.account_id,a.code,f.moneda,
       f.date_due as fecha,
       f.numero_comprobante as comprobante,
       m.venta as precio,
       f.monto_factura / m.venta      as importe,
       f.monto_factura as montofactura,
       (
         select venta
         from res_currency_rate
         order by name desc
         limit 1)                     as cierre,
       f.monto_factura +
       (f.monto_factura * (M.venta - (
         select venta
         from res_currency_rate
         order by name desc
         limit 1)))                   as total,
       f.monto_factura * (M.venta -
                          (
                            select venta
                            from res_currency_rate
                            order by name desc
                            limit 1)) as ajuste

from
     account_account a left join account_move_line ml on ml.id = a.id left join account_invoice f on f.account_id = a.id left join res_currency_rate m ON f.account_id = m.id
where f.state = 'open' and a.corrida is true and f.moneda = 'USD'
        """
        return query
