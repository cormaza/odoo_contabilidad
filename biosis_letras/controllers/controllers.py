# -*- coding: utf-8 -*-
from odoo import http

# class BiosisLetras(http.Controller):
#     @http.route('/biosis_letras/biosis_letras/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_letras/biosis_letras/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_letras.listing', {
#             'root': '/biosis_letras/biosis_letras',
#             'objects': http.request.env['biosis_letras.biosis_letras'].search([]),
#         })

#     @http.route('/biosis_letras/biosis_letras/objects/<model("biosis_letras.biosis_letras"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_letras.object', {
#             'object': obj
#         })