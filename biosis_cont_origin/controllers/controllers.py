# -*- coding: utf-8 -*-
from odoo import http

# class BiosisCont(http.Controller):
#     @http.route('/biosis_cont/biosis_cont/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_cont/biosis_cont/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_cont.listing', {
#             'root': '/biosis_cont/biosis_cont',
#             'objects': http.request.env['biosis_cont.biosis_cont'].search([]),
#         })

#     @http.route('/biosis_cont/biosis_cont/objects/<model("biosis_cont.biosis_cont"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_cont.object', {
#             'object': obj
#         })