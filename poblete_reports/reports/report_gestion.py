# coding=utf-8

from odoo import models, fields, api, tools
import odoo.addons.decimal_precision as dp


class ReportGestion(models.Model):
    _name = 'suscription.gestion.report'
    _auto = False

    subscription_id = fields.Many2one('sale.subscription', u'Suscripción', readonly=True)
    nombre = fields.Char(u'Referencia de suscripción', readonly=True)
    sub_state = fields.Selection([('draft', 'Nuevo'), ('open', 'En progreso'), ('pending', 'Para renovar'),
                                  ('close', 'Cerrado'), ('cancel', 'Cancelado')], readonly=True)
    inv_state = fields.Selection([('open', 'Facturado'), ('paid', 'Pagado')])
    partner_id = fields.Many2one('res.partner', u'Cliente', readonly=True)
    total_sin_igv = fields.Float(u'Total por pagar (sin IGV)', readonly=True, digits=dp.get_precision('Account'))
    total_igv = fields.Float(u'Total IGV por pagar', readonly=True, digits=dp.get_precision('Account'))
    total_mora = fields.Float(u'Total de mora', readonly=True, digits=dp.get_precision('Account'))
    dias_mora = fields.Integer(u'Días de mora', readonly=True)
    inv_mes = fields.Char(u'Mes',readonly=True)

    def _select(self):
        return """
            MIN(sub.id) as id,
            MIN(sub.state) as sub_state,
            sub.id as subscription_id,
            date_part('month',inv.date_invoice) as inv_mes,
            MIN(sub_line.name) as nombre,
            MIN(analytic.partner_id) as partner_id,
            SUM(inv.amount_untaxed) as total_sin_igv,
            SUM(inv.amount_tax) as total_igv,
            MIN(inv.state) as inv_state,
            SUM(sub.amount_mora) as total_mora,
            SUM(sub.amount_mora) / 5 as dias_mora
            """

    def _from(self):
        return """
            sale_subscription sub
            INNER JOIN sale_subscription_line sub_line on sub.id = sub_line.analytic_account_id
            INNER JOIN account_analytic_account analytic ON sub.analytic_account_id = analytic.id
            LEFT JOIN account_invoice inv ON inv.origin = analytic.code AND inv.state IN ('open','paid')
            """

    def _group_by(self):
        return """
            sub.id, date_part('month',inv.date_invoice)
        """

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                SELECT
                %s
                FROM ( %s )
                GROUP BY
                %s
                )""" % (self._table, self._select(), self._from(), self._group_by()))
