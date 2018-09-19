# -*- coding: utf-8 -*-
from odoo import http

# class BiosisMoras(http.Controller):
#     @http.route('/biosis_moras/biosis_moras/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_moras/biosis_moras/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_moras.listing', {
#             'root': '/biosis_moras/biosis_moras',
#             'objects': http.request.env['biosis_moras.biosis_moras'].search([]),
#         })

#     @http.route('/biosis_moras/biosis_moras/objects/<model("biosis_moras.biosis_moras"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_moras.object', {
#             'object': obj
#         })