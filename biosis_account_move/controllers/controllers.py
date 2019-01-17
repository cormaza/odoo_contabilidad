# -*- coding: utf-8 -*-
from odoo import http

# class BiosisAccountMove(http.Controller):
#     @http.route('/biosis_account_move/biosis_account_move/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_account_move/biosis_account_move/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_account_move.listing', {
#             'root': '/biosis_account_move/biosis_account_move',
#             'objects': http.request.env['biosis_account_move.biosis_account_move'].search([]),
#         })

#     @http.route('/biosis_account_move/biosis_account_move/objects/<model("biosis_account_move.biosis_account_move"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_account_move.object', {
#             'object': obj
#         })