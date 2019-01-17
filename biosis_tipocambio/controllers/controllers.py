# -*- coding: utf-8 -*-
from odoo import http

# class BiosisTipocambio(http.Controller):
#     @http.route('/biosis_tipocambio/biosis_tipocambio/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_tipocambio/biosis_tipocambio/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_tipocambio.listing', {
#             'root': '/biosis_tipocambio/biosis_tipocambio',
#             'objects': http.request.env['biosis_tipocambio.biosis_tipocambio'].search([]),
#         })

#     @http.route('/biosis_tipocambio/biosis_tipocambio/objects/<model("biosis_tipocambio.biosis_tipocambio"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_tipocambio.object', {
#             'object': obj
#         })