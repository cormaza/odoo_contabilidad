# -*- coding: utf-8 -*-
from odoo import http

# class SbcSecuencias(http.Controller):
#     @http.route('/sbc_secuencias/sbc_secuencias/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sbc_secuencias/sbc_secuencias/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sbc_secuencias.listing', {
#             'root': '/sbc_secuencias/sbc_secuencias',
#             'objects': http.request.env['sbc_secuencias.sbc_secuencias'].search([]),
#         })

#     @http.route('/sbc_secuencias/sbc_secuencias/objects/<model("sbc_secuencias.sbc_secuencias"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sbc_secuencias.object', {
#             'object': obj
#         })