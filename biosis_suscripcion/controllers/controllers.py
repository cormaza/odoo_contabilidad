# -*- coding: utf-8 -*-
from odoo import http

# class BiosisSuscripcion(http.Controller):
#     @http.route('/biosis_suscripcion/biosis_suscripcion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_suscripcion/biosis_suscripcion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_suscripcion.listing', {
#             'root': '/biosis_suscripcion/biosis_suscripcion',
#             'objects': http.request.env['biosis_suscripcion.biosis_suscripcion'].search([]),
#         })

#     @http.route('/biosis_suscripcion/biosis_suscripcion/objects/<model("biosis_suscripcion.biosis_suscripcion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_suscripcion.object', {
#             'object': obj
#         })