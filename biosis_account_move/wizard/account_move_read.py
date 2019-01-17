import logging

from datetime import datetime, date
import xlrd
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMoveRead(models.Model):
    _name = 'account.move.read'

    fichero = fields.Binary(string='Excel', required=True)
    company_id = fields.Many2one('res.company', string=u'Compania', default=lambda self: self.env.user.company_id)

    @api.multi
    def importar(self):
        self.ensure_one()
        xls_base64 = self.fichero
        wb = xlrd.open_workbook(file_contents=base64.decodestring(xls_base64))

        for sheet in wb.sheets():
            hoja = sheet
            self.procesar_hoja(sheet)



    def procesar_hoja(self,sheet):
        a = sheet.cell(0, 1).value
        self._procesar_datos(0, sheet.nrows,sheet.ncols, sheet)

    def _procesar_datos(self, inicio, fin, columnas, sheet):
        fila_nombre = None
        fila_total = None

        array = []
        arreglo = []
        lines = 0
        moves = 0
        for i in range(inicio, fin):
            if sheet.cell(i, 8).value != 'TOTAL':
                if sheet.cell(i, 6).value == "" or sheet.cell(i, 6).value == "CODIGO" or sheet.cell(i, 6).value == "CUENTA CONTABLE ASOCIADA":
                    pass
                else:
                    if sheet.cell(i, 6).value != "" or sheet.cell(i, 6).value != 'CODIGO':
                        lines = lines + 1
                        numero_registro = sheet.cell(i, 0).value
                        fecha = sheet.cell(i, 1).value
                        dia = fecha[0:2]
                        mes = fecha[3:5]
                        anho = fecha[6:8]
                        anio = str('20' + anho)
                        fecha_op = '-'.join((anio, mes, dia))

                        descripcion = sheet.cell(i, 2).value
                        numero = sheet.cell(i, 4).value
                        fecha_operacion = sheet.cell(i,5).value
                        codigo = sheet.cell(i,6).value
                        debito = sheet.cell(i,9).value or 0.0
                        credito = sheet.cell(i,10).value or 0.0

                        cuenta_id = self.env['account.account'].search([('code','=',codigo),('company_id','=',self.company_id.id)]).id

                        if cuenta_id:
                            moves = moves + 1
                            move = {
                                'name': descripcion + ' / '+ numero ,
                                'account_id': cuenta_id,
                                'debit': debito,
                                'credit': credito,
                                'partner_id': self.company_id.id,
                                'date': fecha_op
                            }
                            arreglo.append(move)
            else:
                if sheet.cell(i, 8).value == 'TOTAL':
                    sw = 0
                    for data in arreglo:
                        account_id = data['account_id']
                        journal_id = self.env['account.journal'].search([('default_debit_account_id', '=', account_id),
                                                                         ('company_id', '=', self.company_id.id)]).id
                        if journal_id == False:
                            journal_id = self.env['account.journal'].search(
                                [('default_credit_account_id', '=', account_id),
                                 ('company_id', '=', self.company_id.id)]).id

                        if journal_id:
                            sw = 1
                            break

                    if sw == 1:
                        for data in arreglo:
                            array.append((0, 0, data))

                        if lines == moves:
                            lines = 0
                            moves = 0
                            self.proceso_move(journal_id, array, fecha_op, numero_registro)
                        else:
                            lines = 0
                            moves = 0
                            array = []
                            arreglo = []
                        #result =
                    else:
                        pass

                    array = []
                    arreglo = []
                else:
                    pass

    def proceso_move(self,journal_id,array,fecha,numero_registro):
        move_vals = {
            'ref': 'Numero registro:' + numero_registro,
            'date': fecha,
            'journal_id': journal_id,
            'line_ids': array
        }
        move = self.env['account.move'].create(move_vals)
        move.post()
        return True
