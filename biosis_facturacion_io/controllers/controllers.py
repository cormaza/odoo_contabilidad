# -*- coding: utf-8 -*-
from odoo import http

# class BiosisFacturacionIo(http.Controller):
#     @http.route('/biosis_facturacion_io/biosis_facturacion_io/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_facturacion_io/biosis_facturacion_io/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_facturacion_io.listing', {
#             'root': '/biosis_facturacion_io/biosis_facturacion_io',
#             'objects': http.request.env['biosis_facturacion_io.biosis_facturacion_io'].search([]),
#         })

#     @http.route('/biosis_facturacion_io/biosis_facturacion_io/objects/<model("biosis_facturacion_io.biosis_facturacion_io"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_facturacion_io.object', {
#             'object': obj
#         })