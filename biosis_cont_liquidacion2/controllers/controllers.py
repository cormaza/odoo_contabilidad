# -*- coding: utf-8 -*-
from odoo import http

# class BiosisContLiquidacion(http.Controller):
#     @http.route('/biosis_cont_liquidacion/biosis_cont_liquidacion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_cont_liquidacion/biosis_cont_liquidacion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_cont_liquidacion.listing', {
#             'root': '/biosis_cont_liquidacion/biosis_cont_liquidacion',
#             'objects': http.request.env['biosis_cont_liquidacion.biosis_cont_liquidacion'].search([]),
#         })

#     @http.route('/biosis_cont_liquidacion/biosis_cont_liquidacion/objects/<model("biosis_cont_liquidacion.biosis_cont_liquidacion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_cont_liquidacion.object', {
#             'object': obj
#         })