# -*- coding: utf-8 -*-
from odoo import http

# class BiosisCubso(http.Controller):
#     @http.route('/biosis_cubso/biosis_cubso/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_cubso/biosis_cubso/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_cubso.listing', {
#             'root': '/biosis_cubso/biosis_cubso',
#             'objects': http.request.env['biosis_cubso.biosis_cubso'].search([]),
#         })

#     @http.route('/biosis_cubso/biosis_cubso/objects/<model("biosis_cubso.biosis_cubso"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_cubso.object', {
#             'object': obj
#         })