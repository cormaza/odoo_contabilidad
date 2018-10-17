# -*- coding: utf-8 -*-
from odoo import http

# class CrmSbc(http.Controller):
#     @http.route('/crm_sbc/crm_sbc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_sbc/crm_sbc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_sbc.listing', {
#             'root': '/crm_sbc/crm_sbc',
#             'objects': http.request.env['crm_sbc.crm_sbc'].search([]),
#         })

#     @http.route('/crm_sbc/crm_sbc/objects/<model("crm_sbc.crm_sbc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_sbc.object', {
#             'object': obj
#         })