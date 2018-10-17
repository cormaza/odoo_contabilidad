# coding=utf-8
from odoo import models, fields, api


class ReportFacturacionWizard(models.TransientModel):
    _name = 'report.liquidacioncompra.wizard'

    @api.model
    def _default_mode_company(self):
        configs = self.env['base.config.settings'].search([('id', '!=', None)])
        config = configs[-1]
        if config.group_multi_company:
            return True
        else:
            return False

    company_id = fields.Many2one('res.company', string=u'Compañía', default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Desde:')
    date_to = fields.Date(string='Hasta:')


    @api.multi
    def print_reportliquidacioncompra_xls(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/reports/report_liquidacioncompra?fecha_inicio='+ self.date_from +'&fecha_fin='+ self.date_to+'',
            #'url': '/reports/report_liquidacioncompra',
            'target': 'new'
        }
