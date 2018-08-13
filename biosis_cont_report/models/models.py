# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from odoo import models, fields, api

# class customaddons/biosis_cont_report(models.Model):
#     _name = 'customaddons/biosis_cont_report.customaddons/biosis_cont_report'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class LibroElectronico(models.Model):
    _name = 'biosis_cont_report.libro.electronico'
    _description = 'Libro Electronicos'
    _rec_name = 'descripcion'
    name = fields.Char(string=u'Nombre',required=True)
    descripcion = fields.Char(string=u'Descripción',required=True)
    codigo_le = fields.Char(string=u'Código LE',required=True)
    state = fields.Selection([('enable','Disponible'),('disable','No disponible')],string=u'Estado Libro')
    nro_orden = fields.Char(string=u'Número Orden')
    account_report_id = fields.Many2one('account.financial.report', 'Reporte Asignado')
    grupo_libro_id = fields.Many2one('biosis_cont_report.grupolibroelectronico', string=u'Grupo Libro Electrónico')

    @api.multi
    @api.depends('nro_orden','descripcion')
    def name_get(self):
        result = []
        for table in self:
            #l_name = table.nro_orden+' - '+table.descripcion
            l_name = table.descripcion
            result.append((table.id, l_name))
        return result

class AccountFinancialReport(models.Model):
    _inherit = 'account.financial.report'
    code = fields.Char(string=u'Código')


class FechasMaximasAtraso(models.Model):
    _name = 'biosis_cont_report.fechasatraso'
    _description = 'Tabla para almacenar fechas para definir atraso en entrega de libros e.'
    _rec_name = 'year'
    year = fields.Selection([(num, str(num)) for num in range(datetime.now().year, datetime.now().year-10, -1)], u'Año', required=True)
    january = fields.Date(string=u'Enero:', required=True)
    february = fields.Date(string=u'Febrero:', required=True)
    march = fields.Date(string=u'Marzo:', required=True)
    april = fields.Date(string=u'Abril:', required=True)
    may = fields.Date(string=u'Mayo:', required=True)
    june = fields.Date(string=u'Junio:', required=True)
    july = fields.Date(string=u'Julio:', required=True)
    august = fields.Date(string=u'Agosto:', required=True)
    september = fields.Date(string=u'Setiembre:', required=True)
    october = fields.Date(string=u'Octubre:', required=True)
    november = fields.Date(string=u'Noviembre:', required=True)
    december = fields.Date(string=u'Diciembre:', required=True)

class GrupoLibroElectronico(models.Model):
    _name = 'biosis_cont_report.grupolibroelectronico'
    _descripcion = 'Grupo Libro Electronico'

    name = fields.Char(string=u'Nombre Grupo Libro',required=True)
    code = fields.Char(string=u'Código', required=True)
    type_time = fields.Selection([('MES','MES'),('DIA','DIA')],string=u'Tipo de tiempo', required=True)
    quantity = fields.Integer(string=u'Cantidad', required=True)