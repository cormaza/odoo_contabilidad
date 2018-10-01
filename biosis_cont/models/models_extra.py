# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from odoo import models, fields, api

"""
    Tablas ANEXO 3 SUNAT
"""
class PleAnexo3Tabla1(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla1'
    _description = u'TABLA 1: TIPO DE MEDIO DE PAGO'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°',required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla2(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla2'
    _description = u'TABLA 2: TIPO DE DOCUMENTO DE IDENTIDAD'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°',required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla3(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla3'
    _description = u'TABLA 3: ENTIDAD FINANCIERA'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°',required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla4(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla4'
    _description = u'TABLA 4: TIPO DE MONEDA'
    _rec_name = 'descripcion'

    cod = fields.Char(string=u'Código')
    descripcion = fields.Char(string=u'Descripción',required=True)
    pais_zona = fields.Char(string=u'País o zona de referencia', required=True)

class PleAnexo3Tabla5(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla5'
    _description = u'TABLA 5: TIPO DE EXISTENCIA'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla6(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla6'
    _description = u'TABLA 6: CÓDIGO DE LA UNIDAD DE MEDIDA'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla8(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla8'
    _description = u'TABLA 8: CÓDIGO DEL LIBRO O REGISTRO'
    _rec_name = 'descripcion'

    code = fields.Char(string=u'CÓDIGO', required=True)
    descripcion = fields.Char(string=u'Nombre o Descripción', required=True)

class PleAnexo3Tabla10(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla10'
    _description = u'TABLA 10: TIPO DE COMPROBANTE DE PAGO O DOCUMENTO'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla11(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla11'
    _description = u'TABLA 11: CÓDIGO DE LA ADUANA'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla12(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla12'
    _description = u'TABLA 12: TIPO DE OPERACIÓN'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla13(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla13'
    _description = u'TABLA 13: CATÁLOGO DE EXISTENCIAS'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)


class PleAnexo3Tabla15(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla15'
    _description = u'TABLA 15: TIPO DE TÍTULO'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla16(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla16'
    _description = u'TABLA 16: TIPO DE ACCIONES O PARTICIPACIONES'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla17(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla17'
    _description = u'TABLA 17: PLAN DE CUENTAS'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla18(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla18'
    _description = u'TABLA 18: TIPO DE ACTIVO FIJO'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla19(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla19'
    _description = u'TABLA 19: ESTADO DEL ACTIVO FIJO'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla20(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla20'
    _description = u'TABLA 20: MÉTODO DE DEPRECIACIÓN'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla21(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla21'
    _description = u'TABLA 21: CÓDIGO DE AGRUPAMIENTO DEL COSTO DE PRODUCCIÓN VALORIZADO ANUAL'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla22(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla22'
    _description = u'TABLA 22: CATÁLOGO DE ESTADOS FINANCIEROS'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)

class PleAnexo3Tabla25(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla25'
    _description = u'TABLA 25 "CONVENIOS PARA EVITAR LA DOBLE TRIBUTACIÓN"'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)


class PleAnexo3Tabla27(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla27'
    _description = u'TABLA 27 "TIPO DE VINCULACION ECONOMICA"'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)
    reglamento_ley = fields.Char(
        string=u'Tipo de vinculación económica según el Reglamento de la Ley del Impuesto a la Renta '
               u'- D.S. N° 122-94-EF y modificatorias')


class PleAnexo3Tabla34(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla34'
    _description = u'TABLA 34: CÓDIGO DE LOS RUBROS DE LOS ESTADOS FINANCIEROS'
    _rec_name = 'descripcion'

    codigo = fields.Char(string=u'Código')
    descripcion = fields.Char(string=u'Descripción', required=True)
    estado_financiero_id = fields.Many2one('biosis.report.ple.anexo3.tabla22',string=u'Estado Finaciero')
    cuentas = fields.Char(string=u'Cuentas a aplicar')
    excepciones = fields.Char(string=u'Cuentas a quitar')
    tipo = fields.Char(string=u'Tipo',required=True)
    padre = fields.Char(string=u'Padre')
    codigo_le = fields.Char(string=u'Libro Electronico',required=True)


class PleAnexo3Tabla35(models.Model):
    _name = 'biosis.report.ple.anexo3.tabla35'
    _description = u'TABLA 35 "PAISES"'
    _rec_name = 'descripcion'

    num_order = fields.Char(string=u'N°', required=True)
    descripcion = fields.Char(string=u'Descripción', required=True)


class ResBank(models.Model):
    _inherit = 'res.bank'

    entidad_financiera_id = fields.Many2one('biosis.report.ple.anexo3.tabla3', string=u'Entidad Financiera')

    @api.multi
    @api.onchange('entidad_financiera_id')
    def onchange_name_bank(self):
        self.name = self.entidad_financiera_id.descripcion

class ProductCategory(models.Model):
    _inherit = 'product.category'

    tipo_existencia = fields.Many2one('biosis.report.ple.anexo3.tabla5', string=u'Tipo de existencia')

class ProductUOM(models.Model):
    _inherit = 'product.uom'

    codigo = fields.Char(string=u'Código Unidad')

class AccountMove(models.Model):
    _inherit = 'account.move'

    # manejo de bonos y acciones ( titulos)
    bono_accion = fields.Boolean(string=u'Bonos y títulos?')
    cod_titulo = fields.Many2one('biosis.report.ple.anexo3.tabla15', string=u'Código del Título')
    val_nom_titulo = fields.Float(string=u'Valor nominal unitario del Título')
    cant_titulos = fields.Integer(string=u'Cantidad de Títulos')


