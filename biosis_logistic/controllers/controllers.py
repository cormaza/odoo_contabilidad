# -*- coding: utf-8 -*-
from odoo import http

# class BiosisLogistic(http.Controller):
#     @http.route('/biosis_logistic/biosis_logistic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_logistic/biosis_logistic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_logistic.listing', {
#             'root': '/biosis_logistic/biosis_logistic',
#             'objects': http.request.env['biosis_logistic.biosis_logistic'].search([]),
#         })

#     @http.route('/biosis_logistic/biosis_logistic/objects/<model("biosis_logistic.biosis_logistic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_logistic.object', {
#             'object': obj
#         })