from odoo import models, fields, api, tools
import odoo.addons.decimal_precision as dp

MES = [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'),
       ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')]


class ReportGestionWizard(models.TransientModel):
    _name = 'report.gestion.wizard'

    mes = fields.Selection(MES, u'Seleccione el mes')

    @api.multi
    def generar_reporte(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/reports/gestion?mes={}'.format(self.mes),
            'target': 'new'
        }

