# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import datetime


class TipoCambioCorrida(models.Model):
    _name = 'tipo.cambio.corrida'
    _description = "Reporte de Corrida"

    reportecorrida_id = fields.Char()
    # mostrar
    # para la consulta
    mes = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')], default='1')
    # years = fields.Integer(string=u'Año')
    years = fields.Selection(
        [('2018', '2018'), ('2019', '2019'), ('2020', '2020'), ('2021', '2021'), ('2022', '2022')], default='2018')
    company_id = fields.Many2one('res.company', string=u'Compañia',
                                 default=lambda self: self.env.user.company_id)
    # years = fields.Integer(string=u'Año')
    #numero_cuenta = fields.Many2one('account.account', string=u'Número Cuenta')

    tipo_cambio_lines = fields.One2many('tipo.cambio.corrida.lines', 'tcc_id', copy=True)

    # tipo_cambio = fields.Float(string=u'Tipo de Cambio', readonly=True)
    # usd = fields.Float(string=u'Importe $', readonly=True)
    # soles = fields.Float(string=u'Importe s/', readonly=True)
    # tc_cierre = fields.Float(string=u'Cierre', readonly=True)
    # total_soles = fields.Float(string=u'Total', readonly=True)
    # ajuste = fields.Float(string=u'Ajuste', readonly=True)
    # numero_cuenta = fields.Char(string=u'Número Cuenta')
    # name = fields.Char(string=u'Nombre')

    def consulta(self):
        mes = int(self.mes)
        anio = int(self.years)
        company_id = self.company_id.id

        query = '''select aml.id, (case when aa.code like '1%' then 'Activo' else 'Pasivo' end) as type,
          aml.date,ai.id, ai.numero_comprobante, ai.move_name, am.name,
          (select aci.numero_comprobante from account_invoice as aci where aci.number like aml.ref and aci.company_id = {2} )
           as new_ref,aml.ref,
          aml.account_id, aa.code,aa.name ,
          round(aml.balance / aml.amount_currency , 3) as tipo_cambio,
          abs(aml.amount_residual_currency) as usd,
          round( abs(aml.amount_residual),3) as soles,
          (case when aa.code like '1%' then
             (select round(rc.venta,3) as venta from res_currency r inner join res_currency_rate rc on r.id = rc.currency_id
          where r.name = 'USD' and extract(MONTH FROM nombre) = {0} and extract(YEAR FROM nombre)= {1} and rc.company_id = {2}
          order by rc.nombre DESC LIMIT 1) else
              (select round(rc.compra,3) as compra from res_currency r inner join res_currency_rate rc on r.id = rc.currency_id
          where r.name = 'USD' and extract(MONTH FROM nombre) = {0} and extract(YEAR FROM nombre)= {1} and rc.company_id = {2}
          order by rc.nombre DESC LIMIT 1)
           end) as tc_cierre,
          (abs(aml.amount_residual_currency) *
          (select round(rc.venta,3) from res_currency r inner join res_currency_rate rc on r.id = rc.currency_id
          where r.name = 'USD' and extract(MONTH FROM nombre) <= {0} and extract(YEAR FROM nombre)= {1} and rc.company_id = {2}
          order by rc.nombre DESC LIMIT 1 )) as total_soles,
          ( abs(aml.amount_residual_currency)  *  (select round(rc.venta,3) from res_currency r inner join res_currency_rate rc on r.id = rc.currency_id
          where r.name = 'USD' and extract(MONTH FROM nombre) <= {0}  and extract(YEAR FROM nombre)= {1} and rc.company_id = {2}
          order by rc.nombre DESC LIMIT 1 ) -  abs(aml.amount_residual) ) as ajuste, aml.currency_id,
          (select nombre from res_currency r
          inner join res_currency_rate rc on r.id = rc.currency_id
          where r.name = 'USD' and extract(MONTH FROM nombre) = 11  and extract(YEAR FROM nombre)= 2018
          order by rc.nombre DESC LIMIT 1 )
          from account_account aa right join account_move_line aml
          on aa.id = aml.account_id left join account_move am on aml.move_id = am.id
          left JOIN account_invoice ai on am.id = ai.move_id
            inner join account_journal aj on aml.journal_id = aj.id
          where aa.corrida is True and extract(MONTH FROM aml.date) <= {0} and extract(YEAR FROM aml.date)= {1}
          and aml.reconciled is NOT true and aa.code not like '10%'
          and aml.company_id = {2} and aj.code != 'CTC' '''.format(int(mes), int(anio), int(company_id))

        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()

        return result

    def consulta_caja(self):
        mes = int(self.mes)
        anio = int(self.years)
        company_id = self.company_id.id

        query = '''select aa.code,SUM(balance) as monto,aml.account_id
                 from account_account aa right join account_move_line aml
                          on aa.id = aml.account_id left join account_move am on aml.move_id = am.id
                          left JOIN account_invoice ai on am.id = ai.move_id
                            inner join account_journal aj on aml.journal_id = aj.id
                          where aa.corrida is True and extract(MONTH FROM aml.date) = {0} and extract(YEAR FROM aml.date)= {1}
                          and aa.code like '10%'
                          and aml.company_id = {2} and aj.code != 'CTC'
                 GROUP BY aa.code,aml.account_id   '''.format(int(mes), int(anio), int(company_id))

        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()

        return result

    def busqueda(self):

        result = self.consulta()
        a = 1
        # pairs = dict(self._cr.fetchall())
        if result:
            for res in result:
                data = {
                    'tcc_id': self.id,
                    'tipo_cambio': res['tipo_cambio'],
                    'usd': res['usd'],
                    'soles': res['soles'],
                    'tc_cierre': res['tc_cierre'],
                    'total_soles': res['total_soles'],
                    'ajuste': res['ajuste'],
                    #'numero_cuenta': res['code'],
                    'name': res['name']
                }
                self.env['tipo.cambio.corrida.lines'].create(data)

                view_id = self.env.ref('biosis_corrida.tipo_cambio_corrida_tree').id
                return {
                    'name': u'Corrida de Tipo de cambio',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'target': 'current',
                    'res_model': 'tipo.cambio.corrida.lines',
                    #'res_id': self.id,
                    'view_id': view_id
                }

            # return {
            #     'type': 'ir.actions.act_window',
            #     'res_model': 'tipo.cambio.corrida.lines',
            #     'view_mode': 'tree',
            #     'view_type': 'form',
            # }

    def generar_asientos(self):
        data = []
        result = self.consulta()
        result_caja = self.consulta_caja()

        data.append(result)
        data.append(result_caja)


        created_moves = self.env['account.move']

        if len(data) > 0:
            journal = self.env['account.journal'].search([('code', '=', 'CTC')])
            activo_debit = 0
            activo_credit = 0
            pasivo_debit = 0
            pasivo_credit = 0

            for dato in result:
                if dato['type'] == 'Activo':
                    if dato['ajuste'] > 0:
                        activo_debit = activo_debit + dato['ajuste']
                    else:
                        activo_credit = activo_credit + dato['ajuste']
                else:
                    if dato['ajuste'] > 0:
                        pasivo_debit = pasivo_debit + dato['ajuste']
                    else:
                        pasivo_credit = pasivo_credit + dato['ajuste']

            activo_debit_caja = 0
            activo_credit_caja = 0

            for dato in result_caja:
                if dato['monto'] > 0:
                    activo_debit_caja = activo_debit_caja + dato['monto']
                else:
                    activo_credit_caja = activo_credit_caja + dato['monto']



            self.asiento_activos(result, journal,activo_debit,activo_credit,result_caja,activo_debit_caja,activo_credit_caja)
            self.asiento_pasivos(result, journal,pasivo_debit,pasivo_credit)
        else:
            pass

    def asiento_activos(self, result, journal,activo_debit,activo_credit,result_caja,activo_debit_caja,activo_credit_caja):
        array = []
        i = 0
        suma = 0

        for dato in result:
            if dato['type'] == 'Activo':
                if dato['ajuste'] < 0:
                    move1 = {}
                    move1 = {
                        'name': dato['numero_comprobante'],
                        'account_id': dato['account_id'],
                        'debit': 0.0,
                        'credit': abs(dato['ajuste']),
                        'journal_id': journal.id,
                        'invoice_id':  dato['id'],
                        'partner_id': self.company_id.id,
                        'date': dato['nombre']
                    }
                else:
                    move1 = {}
                    move1 = {
                        'name': dato['numero_comprobante'],
                        'account_id': dato['account_id'],
                        'debit': abs(dato['ajuste']),
                        'credit': 0.0,
                        'journal_id': journal.id,
                        'invoice_id': dato['id'],
                        'partner_id': self.company_id.id,
                        'date': dato['nombre']
                    }
                fecha = dato['nombre']
                array.append((0, 0, move1))

        for dato in result_caja:

            if dato['monto'] < 0:
                move1 = {}
                move1 = {
                    'name': '/',
                    'account_id': dato['account_id'],
                    'debit': 0.0,
                    'credit': abs(dato['monto']),
                    'journal_id': journal.id,
                    'partner_id': self.company_id.id,
                    'date': fecha
                }
            else:
                move1 = {}
                move1 = {
                    'name': '/',
                    'account_id': dato['account_id'],
                    'debit': abs(dato['monto']),
                    'credit': 0.0,
                    'journal_id': journal.id,
                    'partner_id': self.company_id.id,
                    'date': fecha
                }
            array.append((0, 0, move1))

        destino = 0
        if activo_credit < 0:
            move2= {}
            account_id = journal.default_credit_account_id.id
            if activo_credit_caja < 0:
                debit = abs(activo_credit) + activo_credit_caja
            else:
                debit = abs(activo_credit)
            credit = 0.0

            destino = debit

            move2 = {
                'name': '/',
                'account_id': account_id,
                'debit': debit,
                'credit': credit,
                'journal_id': journal.id,
                'partner_id': self.company_id.id,
                'date': fecha
            }

            array.append((0, 0, move2))

        if activo_debit > 0:
            move2 = {}
            account_id = journal.default_debit_account_id.id
            debit = 0.0
            if activo_debit_caja > 0:
                credit = abs(activo_debit) + activo_debit_caja
            else:
                credit = abs(activo_debit)

            move2 = {
                'name': '/',
                'account_id': account_id,
                'debit': debit,
                'credit': credit,
                'journal_id': journal.id,
                'partner_id': self.company_id.id,
                'date': fecha
            }

            array.append((0, 0, move2))

        val1, val2 = self.asiento_destino(journal,destino,fecha)
        array.append((0, 0, val1))
        array.append((0, 0, val2))

        move_vals = {
            'ref': 'Corrida tipo de cambio Activos mes : ' + self.mes,
            'date': fecha,
            'journal_id': journal.id,
            'line_ids': array
        }
        move = self.env['account.move'].create(move_vals)
        move.post()

        return True


    def asiento_pasivos(self, result,journal,pasivo_debit,pasivo_credit):
        array = []
        i = 0
        suma = 0

        for dato in result:
            if dato['type'] == 'Pasivo':
                if dato['ajuste'] < 0:
                    move1 = {}
                    move1 = {
                        'name': dato['numero_comprobante'],
                        'account_id': dato['account_id'],
                        'debit': 0.0,
                        'credit': abs(dato['ajuste']),
                        'journal_id': journal.id,
                        'invoice_id': dato['id'],
                        'partner_id': self.company_id.id,
                        'date': dato['nombre']
                    }
                else:
                    move1 = {}
                    move1 = {
                        'name': dato['numero_comprobante'],
                        'account_id': dato['account_id'],
                        'debit': abs(dato['ajuste']),
                        'credit': 0.0,
                        'journal_id': journal.id,
                        'invoice_id': dato['id'],
                        'partner_id': self.company_id.id,
                        'date': dato['nombre']
                    }
                fecha = dato['nombre']
                array.append((0, 0, move1))



        if pasivo_credit < 0:
            move2 = {}
            account_id = journal.default_credit_account_id.id
            debit = abs(pasivo_credit)
            credit = 0.0
            destino = debit

            move2 = {
                'name': '/',
                'account_id': account_id,
                'debit': debit,
                'credit': credit,
                'journal_id': journal.id,
                'partner_id': self.company_id.id,
                'date': fecha
            }

            array.append((0, 0, move2))
            val1, val2 = self.asiento_destino(journal, destino, fecha)
            array.append((0, 0, val1))
            array.append((0, 0, val2))

        if pasivo_debit > 0:
            move2 = {}
            account_id = journal.default_debit_account_id.id

            debit = 0.0
            credit = abs(pasivo_debit)

            move2 = {
                'name': '/',
                'account_id': account_id,
                'debit': debit,
                'credit': credit,
                'journal_id': journal.id,
                'partner_id': self.company_id.id,
                'date': fecha
            }

            array.append((0, 0, move2))



        move_vals = {
            'ref': 'Corrida tipo de cambio Pasivos mes : ' + self.mes,
            'date': fecha,
            'journal_id': journal.id,
            'line_ids': array
        }
        move = self.env['account.move'].create(move_vals)
        move.post()

        return True

    def asiento_destino(self,journal,valor,fecha):

        move_destino = {
            'name' : '/',
            'account_id' : journal.account_destino_debit_id.id,
            'debit': valor,
            'credit': 0.0,
            'journal_id': journal.id,
            'partner_id': self.company_id.id,
            'date': fecha
        }

        move_carga={
            'name': '/',
            'account_id': journal.account_destino_credit_id.id,
            'debit': 0.0,
            'credit': valor,
            'journal_id': journal.id,
            'partner_id': self.company_id.id,
            'date': fecha
        }
        return move_destino, move_carga


class TipoCambioCorridaLine(models.Model):
    _name = 'tipo.cambio.corrida.lines'
    _order = "tcc_id,id"

    tcc_id = fields.Many2one('tipo.cambio.corrida', ondelete='cascade', index=True)
    tipo_cambio = fields.Float(string=u'Tipo de Cambio', readonly=True)
    usd = fields.Float(string=u'Importe $', readonly=True)
    soles = fields.Float(string=u'Importe s/', readonly=True)
    tc_cierre = fields.Float(string=u'Cierre', readonly=True)
    total_soles = fields.Float(string=u'Total', readonly=True)
    ajuste = fields.Float(string=u'Ajuste', readonly=True)
    numero_cuenta = fields.Char(string=u'Número Cuenta')
    name = fields.Char(string=u'Nombre')
