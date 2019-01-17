# coding=utf-8
import base64

import xlrd

from odoo import models, api


class ProcesadorMateriales(models.TransientModel):
    _name = 'utils.procesar_materiales'

    @api.multi
    def procesar_libro(self, xls_base64):
        productos = []

        wb = xlrd.open_workbook(file_contents=base64.decodestring(xls_base64))
        for sheet in wb.sheets():
            if sheet.name != 'FORMULARIO':
                productos.append(self._procesar_hoja(sheet))
        print 'PRODUCTOS: \n%s' % '\n'.join([str(producto) for producto in productos])
        return productos

    def _procesar_hoja(self, sheet):
        tipo = 'normal'
        if 'CLOSET' in sheet.cell(0, 1).value.upper():
            # Quiere decir que son closets y tienen un tratamiento especial
            tipo = 'closet'

        producto = {
            'nombre': sheet.cell(0, 1).value,
            'precio': sheet.cell(1, 1).value,
            'tipo': tipo,
            'modulos': self._procesar_modulos(sheet, tipo=tipo)
        }
        return producto

    def _buscar_cabecera_total(self, inicio, fin, sheet):
        fila_nombre = None
        fila_total = None
        for i in range(inicio, fin):
            if sheet.cell(i, 0).value == 'MODULO:' and not fila_nombre:
                fila_nombre = i
            if sheet.cell(i, 0).value == 'Total' and not fila_total:
                fila_total = i
        return fila_nombre, fila_total

    def _procesar_modulos(self, sheet, tipo):
        modulos = []
        fila_nombre, fila_total = self._buscar_cabecera_total(0, sheet.nrows, sheet)
        modulos.append({
            'nombre': sheet.cell(fila_nombre, 1).value,
            'materiales': self._procesar_lista_materiales(sheet, fila_nombre + 2, fila_total),
            'precio': tipo == 'closet' and sheet.cell(fila_nombre + 1, 1).value or 0.0,
            'tipo': tipo
        })
        while fila_total < sheet.nrows - 1:
            fila_nombre, fila_total = self._buscar_cabecera_total(fila_total + 1, sheet.nrows, sheet)
            modulos.append({
                'nombre': sheet.cell(fila_nombre, 1).value,
                'materiales': self._procesar_lista_materiales(sheet, fila_nombre + 2, fila_total),
                'precio': tipo == 'closet' and sheet.cell(fila_nombre + 1, 1).value or 0.0,
                'tipo': tipo
            })
        return modulos

    def _procesar_lista_materiales(self, sheet, fila_materiales, fila_total):
        ldms = []
        materiales_cods = sheet.row_slice(fila_materiales, 5)
        totales = sheet.row_slice(fila_total, 5)

        for i in range(len(materiales_cods)):
            if materiales_cods[i].value and totales[i].value:
                ldms.append({
                    'codigo': '%d' % materiales_cods[i].value,
                    'cantidad': totales[i].value
                })

        return ldms
