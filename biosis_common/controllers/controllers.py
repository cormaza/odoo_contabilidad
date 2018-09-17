# -*- coding: utf-8 -*-
from odoo import http

# class BiosisCommon(http.Controller):
#     @http.route('/biosis_common/biosis_common/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_common/biosis_common/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_common.listing', {
#             'root': '/biosis_common/biosis_common',
#             'objects': http.request.env['biosis_common.biosis_common'].search([]),
#         })

#     @http.route('/biosis_common/biosis_common/objects/<model("biosis_common.biosis_common"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_common.object', {
#             'object': obj
#         })