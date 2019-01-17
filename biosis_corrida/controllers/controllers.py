# -*- coding: utf-8 -*-
from odoo import http

# class BiosisCorrida(http.Controller):
#     @http.route('/biosis_corrida/biosis_corrida/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_corrida/biosis_corrida/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_corrida.listing', {
#             'root': '/biosis_corrida/biosis_corrida',
#             'objects': http.request.env['biosis_corrida.biosis_corrida'].search([]),
#         })

#     @http.route('/biosis_corrida/biosis_corrida/objects/<model("biosis_corrida.biosis_corrida"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_corrida.object', {
#             'object': obj
#         })