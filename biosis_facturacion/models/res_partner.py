# -*- coding: utf-8 -*-
import requests

from odoo import models, fields, api


def obtener_datos(tipo_doc, numero_doc, format='json'):
    user, password = 'demorest', 'demo1234'
    url = 'http://py-devs.com/api'
    url = '%s/%s/%s' % (url, tipo_doc, str(numero_doc))
    res = {'error': True, 'message': None, 'data': {}}
    try:
        response = requests.get(url, auth=(user, password))
    except requests.exceptions.ConnectionError, e:
        res['message'] = 'Error en la conexion'
        return res

    if response.status_code == 200:
        res['error'] = False
        res['data'] = response.json()
    else:
        try:
            res['message'] = response.json()['detail']
        except Exception, e:
            res['error'] = True
    return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    codigo_partner = fields.Char(string=u'Código cliente')

    @api.model
    def create(self, vals):
        catalog_06_id = vals.get('catalog_06_id', False)
        vat = vals.get('vat', False)
        procesar_doc = not catalog_06_id and vat
        if procesar_doc:
            vat = vat.strip()

            if len(vat) == 8:
                # Es un DNI
                td_code = 1
            elif len(vat) == 11:
                # Es RUC
                td_code = 6
            else:
                # Es no documentado
                td_code = 0

            catalog_06_id = self.env['einvoice.catalog.06'].search([('code', '=', td_code)], limit=1).id

            vals.update({'catalog_06_id': catalog_06_id})

        partner = super(ResPartner, self).create(vals)

        if procesar_doc:
            partner.update_document()

            partner.write({'name': partner.name == '-' and partner.registration_name or partner.name})

        return partner
