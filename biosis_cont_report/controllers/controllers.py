# -*- coding: utf-8 -*-
from odoo import http

# class BiosisContReport(http.Controller):
#     @http.route('/biosis_cont_report/biosis_cont_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_cont_report/biosis_cont_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_cont_report.listing', {
#             'root': '/biosis_cont_report/biosis_cont_report',
#             'objects': http.request.env['biosis_cont_report.biosis_cont_report'].search([]),
#         })

#     @http.route('/biosis_cont_report/biosis_cont_report/objects/<model("biosis_cont_report.biosis_cont_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_cont_report.object', {
#             'object': obj
#         })