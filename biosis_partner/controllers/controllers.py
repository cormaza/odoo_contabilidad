# -*- coding: utf-8 -*-
from odoo import http

# class BiosisPartner(http.Controller):
#     @http.route('/biosis_partner/biosis_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_partner/biosis_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_partner.listing', {
#             'root': '/biosis_partner/biosis_partner',
#             'objects': http.request.env['biosis_partner.biosis_partner'].search([]),
#         })

#     @http.route('/biosis_partner/biosis_partner/objects/<model("biosis_partner.biosis_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_partner.object', {
#             'object': obj
#         })