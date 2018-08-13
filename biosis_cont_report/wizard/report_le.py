# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, datetime

class AccountLibroElectronicoReport(models.TransientModel):
    _name = "biosis_cont_report.report.le"
    _description = u"Reporte Libros Electrónicos"

    libro_electronico = fields.Many2one('biosis_cont_report.libro.electronico',string=u'Libro Electrónico',required=True)
    mes = fields.Selection([('01', u'Enero'),
                              ('02', u'Febrero'),
                              ('03', u'Marzo'),
                              ('04', u'Abril'),
                              ('05', u'Mayo'),
                              ('06', u'Junio'),
                              ('07', u'Julio'),
                              ('08', u'Agosto'),
                              ('09', u'Setiembre'),
                              ('10', u'Octubre'),
                              ('11', u'Noviembre'),
                              ('12', u'Diciembre')],'Mes')

    year = fields.Selection([(num, str(num)) for num in range((datetime.now().year), 1900,-1 )], u'Año')

    @api.multi
    def print_report_txt(self):
        data = {}
        data['form'] = self.read(['mes', 'year', 'libro_electronico'])[0]

        return {'type': 'ir.actions.report.xml',
                'report_name': 'biosis_cont.report_ple.txt',
                'datas': data['form'],
                'name': u'PLE'
            }

    @api.multi
    def get_ple_file(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/biosis_cont/contabilidad/ple?mes=%s&year=%s&tipo_reporte=%s&filename=Reporte_PLE.txt' % (self.mes,self.year,self.tipo_reporte),
            'target': 'self',
        }

