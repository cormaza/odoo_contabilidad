# -*- coding: utf-8 -*-
import datetime
import re
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class Ple_3_7(models.Model):
    _name = 'account.ple.3.7'
    _description = u'PLE - DETALLE DEL SALDO DE LA CUENTA 20 - MERCADERIAS Y LA CUENTA 21 - PRODUCTOS TERMINADOS'

    periodo_1 = fields.Char(string=u'Periodo', required=True)
    cod_catalago_2 = fields.Char(string=u'Código del catálogo utilizado', required=True) #tabla 13
    tipo_exist_3 = fields.Char(string=u'Tipo de existencia', required=True) #tabla 5
    cod_exist_4 = fields.Char(string=u'Código propio de la existencia', default=u'')
    cod_exist_osce_5 = fields.Char(string=u'Código de la existencia, de acuerdo al Catálogo Único de Bienes, Servicios y Obras', default=u'')
    descrp_exist_6 = fields.Char(string=u'Descripción de la existencia', default=u'')
    cod_unit_7 = fields.Char(string=u'Código de la Unidad de medida de la existencia', required=True) #tabla 16
    cod_val_8 = fields.Char(string=u'Código del método de valuación utilizado', required=True) #tabla 14
    cant_exist_9 = fields.Char(string=u'Cantidad de la existencia', required=True)
    cost_unit_exist_10 = fields.Char(string=u'Costo unitario de la existencia', required=True)
    cost_total_11 = fields.Char(string=u'Costo total', required=True)
    estado_12 = fields.Char(string=u'Estado', required=True)
    product_id = fields.Many2one('product.product', string=u'Producto')
    company_id = fields.Many2one('res.company', required=True, string=u"Compañia")

    @api.multi
    def get_ple_line(self):
        return self.periodo_1 + '|' + self.cod_catalago_2 + '|' + self.tipo_exist_3 + '|' + self.cod_exist_4 + '|' + self.cod_exist_osce_5 + '|' \
               + self.descrp_exist_6 + '|' + self.cod_unit_7 + '|' + self.cod_val_8 + '|' + self.cant_exist_9 + '|' \
               + self.cost_unit_exist_10 + '|' + self.cost_total_11 + '|' + self.estado_12 + '|' + '\n'

    @api.multi
    def get_ple(self, company_id, fecha_reporte, fecha_inicio, fecha_fin):
        ple_res = ''
        fecha_reporte_anio = str(fecha_fin.year) + '12' + '31'
        ple_list = []
        ple_update = []
        ple_new = []

        stock_quant_list = self.env['stock.quant'].search([
            ('qty','>=',0),
            ('company_id','=',company_id.id)
        ]).sorted(key=lambda r:int(r.product_id.id))

        ple_list = self.env['account.ple.3.7'].search([
            ('periodo_1', '=', fecha_reporte_anio),
            ('company_id', '=', company_id.id)
        ])

        stock_quant_ple = [line.product_id for line in ple_list]

        if len(ple_list) > 0:
            for line_ml in stock_quant_list:
                if not (line_ml in stock_quant_ple):
                    ple_new.append(line_ml)
                else:
                    ple_update.append(line_ml)
        else:
            ple_new = stock_quant_list

        if len(ple_new) > 0:
            ple_nuevos = self.create_ple_items(company_id, ple_new, fecha_reporte, fecha_inicio, fecha_fin)
            ple_res = ple_res + ple_nuevos

        if len(ple_update) > 0:
            ple_modificados = self.update_ple_items(company_id, ple_update, fecha_reporte, fecha_inicio, fecha_fin)
            ple_res = ple_res + ple_modificados

        return ple_res

    @api.multi
    def create_ple_items(self, company_id, ple_new, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        ple_model = self.env['account.ple.3.7']
        periodo = str(fecha_fin.year) + '12' + '31'
        i = 1
        for line in ple_new:
            if datetime.date.today() <= self.get_fecha_atraso(fecha_fin):
                ple_item_estado = u'1'
            elif datetime.date.today() > self.get_fecha_atraso(fecha_fin):
                ple_item_estado = u'8'
            ple_item_vals = {
                'periodo_1': periodo,
                'cod_catalago_2': '1',
                'tipo_exist_3': line.product_id.product_tmpl_id.categ_id.tipo_existencia.num_order,
                'cod_exist_4': line.product_id.product_tmpl_id.default_code if line.product_id.product_tmpl_id.default_code else '00000',
                'cod_exist_osce_5': line.product_id.product_tmpl_id.codigo_cubso.codigo,
                'descrp_exist_6': line.product_id.product_tmpl_id.name,
                'cod_unit_7': line.product_id.product_tmpl_id.uom_id.codigo,
                'cod_val_8': line.product_id.product_tmpl_id.codigo_valuacion.num_order,
                'cant_exist_9': str(line.qty),
                'cost_unit_exist_10': str(line.product_id.product_tmpl_id.standard_price),
                'cost_total_11': str(line.product_id.product_tmpl_id.standard_price*line.qty),
                'estado_12': ple_item_estado,
                'product_id': line.product_id.id,
                'company_id': company_id.id,
            }
            ple_item = ple_model.create(ple_item_vals)
            ple_items = ple_items + ple_item.get_ple_line()
            i = i + 1
        return ple_items

    @api.multi
    def update_ple_items(self, company_id, ple_update, fecha_reporte, fecha_inicio, fecha_fin):
        ple_items = ''
        for line in ple_update:
            ple_actual = self.env['account.ple.3.7'].search([
                ('product_id', '=', line.product_id)
            ])
            if ple_actual.create_date < line.write_date:
                estado_ple = u'1' if datetime.date.today() <= self.get_fecha_atraso(fecha_fin) else u'9'
                ple_item_vals = {
                    'tipo_exist_3': line.product_id.product_tmpl_id.categ_id.tipo_existencia.num_order,
                    'cod_exist_4': line.product_id.product_tmpl_id.default_code if line.product_id.product_tmpl_id.default_code else '00000',
                    'cod_exist_osce_5': line.product_id.product_tmpl_id.codigo_cubso.codigo,
                    'descrp_exist_6': line.product_id.product_tmpl_id.name,
                    'cod_unit_7': line.product_id.product_tmpl_id.uom_id.codigo,
                    'cod_val_8': line.product_id.product_tmpl_id.codigo_valuacion.num_order,
                    'cant_exist_9': str(line.qty),
                    'cost_unit_exist_10': str(line.product_id.product_tmpl_id.standard_price),
                    'cost_total_11': str(line.product_id.product_tmpl_id.standard_price*line.qty),
                    'estado_12': estado_ple,
                    'company_id': company_id.id
                }
                ple_actual.write(ple_item_vals)
                ple_items = ple_items + ple_actual.get_ple_line()
            else:
                ple_items = ple_items + ple_actual.get_ple_line()
        return ple_items

    def get_fecha_atraso(self, fecha_fin):
        grupo_libro = self.env['biosis_cont_report.grupolibroelectronico'].search([
            ('code', '=', '3')
        ], limit=1)
        if grupo_libro.type_time == 'MES':
            fecha_maxima = fecha_fin + relativedelta(months=int(grupo_libro.quantity))
        else:
            fecha_maxima = fecha_fin + relativedelta(days=int(grupo_libro.quantity))
        return fecha_maxima