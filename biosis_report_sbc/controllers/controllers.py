# -*- coding: utf-8 -*-
from odoo import http

# class BiosisReportSbcLiquidacion(http.Controller):
#     @http.route('/biosis_report_sbc_liquidacion/biosis_report_sbc_liquidacion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_report_sbc_liquidacion/biosis_report_sbc_liquidacion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_report_sbc_liquidacion.listing', {
#             'root': '/biosis_report_sbc_liquidacion/biosis_report_sbc_liquidacion',
#             'objects': http.request.env['biosis_report_sbc_liquidacion.biosis_report_sbc_liquidacion'].search([]),
#         })

#     @http.route('/biosis_report_sbc_liquidacion/biosis_report_sbc_liquidacion/objects/<model("biosis_report_sbc_liquidacion.biosis_report_sbc_liquidacion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_report_sbc_liquidacion.object', {
#             'object': obj
#         })