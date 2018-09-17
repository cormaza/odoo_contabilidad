# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Ple_3_17(models.Model):
    _name = 'account.ple.3.17'
    _description = u'PLE para Balance de Comprobación'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    codigo_cuenta_2 = fields.Char(string=u'Código Cuenta Contable', required=True)
    saldos_iniciales_d_3 = fields.Char(string=u'Saldos Iniciales Debe', required=True, default=u'0.00')
    saldos_iniciales_h_4 = fields.Char(string=u'Saldos Iniciales Haber', required=True, default=u'0.00')
    mov_ejer_d_5 = fields.Char(string=u'Movimientos del ejercicio - Debe', required=True, default=u'0.00')
    mov_ejer_h_6 =fields.Char(string=u'Movimientos del ejercicio - Haber', required=True, default=u'0.00')
    sumas_mayor_d_7 = fields.Char(string=u'Sumas del Mayor - Debe', required=True, default=u'0.00')
    sumas_mayor_h_8 = fields.Char(string=u'Sumas del Mayor - Haber', required=True, default=u'0.00')
    saldos_31_dic_de_9 = fields.Char(string=u'Saldos al 31 de Diciembre - Deudor', required=True, default=u'0.00')
    saldos_31_dic_ac_10 = fields.Char(string=u'Saldos al 31 de Diciembre - Acreedor', required=True, default=u'0.00')
    transf_cancel_d_11 = fields.Char(string=u'Transferencias y Cancelaciones - Debe', required=True, default=u'0.00')
    transf_cancel_h_12 = fields.Char(string=u'Transferencias y Cancelaciones - Haber', required=True, default=u'0.00')
    cuenta_balance_a_13 = fields.Char(string=u'Cuentas de Balance - Activo', required=True, default=u'0.00')
    cuenta_balance_p_14 = fields.Char(string=u'Cuentas de Balance - Pasivo', required=True, default=u'0.00')
    resul_nat_perd_15 = fields.Char(string=u'Resultado por Naturaleza - Pérdidas', required=True, default=u'0.00')
    resul_nat_gan_16 = fields.Char(string=u'Resultado por Naturaleza - Ganancias', required=True, default=u'0.00')
    adiciones_17 = fields.Char(string=u'Adiciones', required=True)
    deducciones_18 = fields.Char(string=u'Deducciones', required=True)
    estado_19 = fields.Char(string=u'Estado', required=True)
    campo_libre_20 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_21 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_22 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_23 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_24 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_25 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_26 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_27 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_28 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_29 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_30 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_31 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_32 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_33 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_34 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_35 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_36 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_37 = fields.Char(string=u'Campo Libre', size=200)
    campo_libre_38 = fields.Char(string=u'Campo Libre', size=200)
    usa_campos = fields.Boolean(string=u'Usar campos libres', default=False)
    tipo_envio = fields.Selection([('ANUAL', 'Anual'), ('MENSUAL', 'Mensual')],
                                    string='Tipo Envio', required=True, default="MENSUAL")
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.codigo_cuenta_2 + '|' + self.saldos_iniciales_d_3 + '|' + self.saldos_iniciales_h_4 + '|' \
               + self.mov_ejer_d_5 + '|' + self.mov_ejer_h_6 + '|' + self.sumas_mayor_d_7 + '|' + self.sumas_mayor_h_8 + '|' \
               + self.saldos_31_dic_de_9 + '|' + self.saldos_31_dic_ac_10 + '|' + self.transf_cancel_d_11 + '|'+ self.transf_cancel_h_12 + '|' \
               + self.cuenta_balance_a_13 + '|' + self.cuenta_balance_p_14 + '|' + self.resul_nat_perd_15 + '|'+ self.resul_nat_gan_16 + '|' \
               + self.adiciones_17 + '|' + self.deducciones_18 + '|' + self.estado_19 + '|'+'\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_bc_res = ''
        fecha_reporte_anio = str(fecha_fin.year)+'12'+'31'
        bc_ple_list = []
        bc_ple_update = []
        bc_ple_old = []
        bc_ple_new = []

        bc_report = self.get_lines_report(company_id, fecha_inicio, fecha_fin) #Lineas de bc segun el periodo ingresado

        bc_ple_list = self.env['account.ple.3.17'].search([
            ('periodo_1','=',fecha_reporte_anio),
            ('company_id','=',company_id.id)
        ])

        if len(bc_ple_list) > 0:
            for line_bc in bc_report:
                for line_ple in bc_ple_list:
                    if line_ple.codigo_cuenta_2 == line_bc['codigo']:
                        if line_ple.sumas_mayor_d_7 != str(line_bc['debit']) or line_ple.sumas_mayor_h_8 != str(line_bc['credit']):
                            bc_ple_update.append(line_bc)
                        else:
                            bc_ple_old.append(line_bc)
                        continue
        else:
            bc_ple_new = bc_report

        if len(bc_ple_list) > 0:
            for line_bc in bc_report:
                if not(line_bc in bc_ple_update) and not(line_bc in bc_ple_old):
                    bc_ple_new.append(line_bc)

        if len(bc_ple_new) > 0:
            """
               Pasos para agregar lineas BC al res
            """
            ple_nuevos = self.create_ple_items(company_id, bc_ple_new, fecha_reporte, fecha_inicio, fecha_fin)
            ple_bc_res = ple_bc_res + ple_nuevos

        if len(bc_ple_list) > 0:
            """
                Pasos para crear lineas Diario Detalle con cuentas_list_new
             """
            ple_old = self.update_ple_items(company_id, bc_ple_old, bc_ple_update, fecha_reporte, fecha_inicio, fecha_fin)
            ple_bc_res = ple_bc_res + ple_old

        return ple_bc_res



    @api.multi
    def create_ple_items(self, company_id, account_lines, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_bc = self.env['account.ple.3.17']
        periodo = str(fecha_fin.year)+'12'+'31'
        for line in account_lines:
            if  datetime.date.today() <= self.get_fecha_atraso(fecha_fin):
                ple_item_estado_19 = u'1'
            elif datetime.date.today() > self.get_fecha_atraso(fecha_fin):
                ple_item_estado_19 = u'8'
            print 'codigo: '+line['codigo']+', debit: '+str(line['debit'])+', credit: '+str(line['credit'])
            ple_item_vals = {
                'periodo_1': periodo,
                'codigo_cuenta_2': line['codigo'],
                'saldos_iniciales_d_3': '0.00', #implementar
                'saldos_iniciales_h_4': '0.00',
                'mov_ejer_d_5': str(line['debit']) if line['debit']>0 else '0.00',
                'mov_ejer_h_6': str(line['credit']) if line['credit']>0 else '0.00',
                'sumas_mayor_d_7': str(line['debit']) if line['debit']>0 else '0.00',
                'sumas_mayor_h_8': str(line['credit']) if line['credit']>0 else '0.00',
                'saldos_31_dic_de_9': str(line['deudor']) if line['deudor']>0 else '0.00',
                'saldos_31_dic_ac_10': str(line['acreedor']) if line['acreedor']>0 else '0.00',
                'transf_cancel_d_11': str(line['tc_debe']) if line['tc_debe']>0 else '0.00',
                'transf_cancel_h_12': str(line['tc_haber']) if line['tc_haber']>0 else '0.00',
                'cuenta_balance_a_13': str(line['activo']) if line['activo']>0 else '0.00',
                'cuenta_balance_p_14': str(line['pasivo']) if line['pasivo']>0 else '0.00',
                'resul_nat_perd_15': str(line['ganancia']) if line['ganancia']>0 else '0.00',
                'resul_nat_gan_16': str(line['perdida']) if line['perdida']>0 else '0.00',
                'adiciones_17': '0.00',
                'deducciones_18': '0.00',
                'estado_19': ple_item_estado_19,
                'company_id': company_id.id
            }
            ple_item = ple_bc.create(ple_item_vals)
            # despues de proceso
            ple_items = ple_items + ple_item.get_ple_line()
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, bc_ple_old, bc_ple_update, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        for line in bc_ple_old:
            ple_item = self.env['account.ple.3.17'].search([
                ('codigo_cuenta_2','=',line['codigo'])
            ],limit=1)
            ple_items = ple_items + ple_item.get_ple_line()

        for line in bc_ple_update:
            ple_item = self.env['account.ple.3.17'].search([
                ('codigo_cuenta_2', '=', line['codigo'])
            ], limit=1)
            estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'

            ple_item_vals = {
                'saldos_iniciales_d_3': '0.00', #hasta que se implemente saldos iniciales
                'saldos_iniciales_h_4': '0.00', #hasta que se implemente saldos iniciales
                'mov_ejer_d_5': str(line['debit']),
                'mov_ejer_h_6': str(line['credit']),
                'sumas_mayor_d_7': str(line['debit']),
                'sumas_mayor_h_8': str(line['credit']),
                'saldos_31_dic_de_9': str(line['deudor']),
                'saldos_31_dic_ac_10': str(line['acreedor']),
                'transf_cancel_d_11': str(line['tc_debe']),
                'transf_cancel_h_12': str(line['tc_haber']),
                'cuenta_balance_a_13': str(line['activo']),
                'cuenta_balance_p_14': str(line['pasivo']),
                'resul_nat_perd_15': str(line['ganancia']),
                'resul_nat_gan_16': str(line['perdida']),
                'adiciones_17': '0.00',
                'deducciones_18': '0.00',
                'estado_19': estado_ple,
                'company_id': company_id.id
            }
            ple_item.write(ple_item_vals)
            ple_items = ple_items + ple_item.get_ple_line()

        return ple_items

    def get_lines_report(self, company_id, fecha_inicio, fecha_fin):
        lines = []
        reporte_balance = self.env['report.biosis_cont_report.balance_comprobacion']  # Reporte financiero(odoo)
        libro_electronico = self.env['biosis_cont_report.libro.electronico'].search([('codigo_le', '=', '031700')], limit=1)
        report_lines = reporte_balance.get_account_lines(self.get_data_report(company_id, libro_electronico, fecha_inicio, fecha_fin))

        for line in report_lines:
            if line['level'] == 4:
                lines.append(line)

        return lines

    def get_data_report(self, company_id, libro_electronico, fecha_inicio, fecha_fin):
        data = {}
        data['account_report_id'] = (libro_electronico.account_report_id.id, libro_electronico.account_report_id.name)
        data['enable_filter'] = False
        data['debit_credit'] = True
        data['used_context'] = {}
        data['used_context']['date_from'] = fecha_inicio.strftime('%Y-%m-%d')
        data['used_context']['date_to'] = fecha_fin.strftime('%Y-%m-%d')
        data['used_context']['lang'] = u'es_PE'
        data['used_context']['state'] = u'posted'
        data['used_context']['strict_range'] = True
        data['used_context']['company'] = company_id.id
        return data

    def get_fecha_atraso(self,fecha_fin):
        grupo_libro = self.env['biosis_cont_report.grupolibroelectronico'].search([
            ('code','=','3')
        ], limit=1)
        if grupo_libro.type_time == 'MES':
            fecha_maxima = fecha_fin + relativedelta(months= int(grupo_libro.quantity))
        else:
            fecha_maxima = fecha_fin + relativedelta(days=int(grupo_libro.quantity))
        return fecha_maxima


