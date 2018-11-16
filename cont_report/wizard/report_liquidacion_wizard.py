# coding=utf-8
from odoo import models, fields, api


class ReportFacturacionWizard(models.TransientModel):
    _name = 'report.liquidacion.wizard'


    @api.multi
    def generar_reporte(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/reports/report_factura',
            'target': 'new'
        }
