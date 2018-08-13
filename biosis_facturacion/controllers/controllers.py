# -*- coding: utf-8 -*-
from odoo import http

# class BiosisFacturacion(http.Controller):
#     @http.route('/biosis_facturacion/biosis_facturacion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_facturacion/biosis_facturacion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_facturacion.listing', {
#             'root': '/biosis_facturacion/biosis_facturacion',
#             'objects': http.request.env['biosis_facturacion.biosis_facturacion'].search([]),
#         })

#     @http.route('/biosis_facturacion/biosis_facturacion/objects/<model("biosis_facturacion.biosis_facturacion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_facturacion.object', {
#             'object': obj
#         })