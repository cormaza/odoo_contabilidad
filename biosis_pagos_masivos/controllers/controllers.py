# -*- coding: utf-8 -*-
from odoo import http

# class BiosisPagosMasivos(http.Controller):
#     @http.route('/biosis_pagos_masivos/biosis_pagos_masivos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biosis_pagos_masivos/biosis_pagos_masivos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biosis_pagos_masivos.listing', {
#             'root': '/biosis_pagos_masivos/biosis_pagos_masivos',
#             'objects': http.request.env['biosis_pagos_masivos.biosis_pagos_masivos'].search([]),
#         })

#     @http.route('/biosis_pagos_masivos/biosis_pagos_masivos/objects/<model("biosis_pagos_masivos.biosis_pagos_masivos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biosis_pagos_masivos.object', {
#             'object': obj
#         })