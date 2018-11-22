# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict, MutableMapping, OrderedDict
from odoo.exceptions import UserError


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# clase pago
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    #_name = 'payment.letra'

    @api.model
    def _get_letra(self):
        letra_id = 0
        if 'active_model' in self._context:
            if self._context['active_model'] == 'account.invoice':
                pass
            else:
                if 'active_id' in self._context:
                    letra_id = self._context['active_id']
                    #letra = self.env['account.letra'].search([('id', '=', letra_id)], limit=1)
                    return letra_id
    # nro correlativo
    num_letra = fields.Char(string=u'Nro de letra', default=_get_letra)
    # nrocorrelativo = fields.Char(string = u'Nro Correlativo de letra',related='num_letra.nrocorrelativo')
    #nrocorrelativo = fields.Char(string = u'Nro Correlativo de letra')
    #monto_letra = fields.Float(strin='Monto Letra')

    def post_pago(self):
        contador = 0
        letra = self.env['account.letra'].search([('num_letra', '=', self.num_letra)], limit=1)
        for invoice_ids in letra.facturas_lineas_ids:
            contador = contador + 1
            invoice = self.env['account.invoice'].search([('id', '=', invoice_ids.factura_relacionada.id)], limit=1)
            # self.post_pagos_moras(invoice_mora)
            data = {
                'payment_type': 'inbound',
                'amount': invoice.residual_signed,
                'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                'partner_type': 'customer',
                'partner_id': invoice.partner_id.id,
                'payment_difference': 0,
                'currency_id': letra.currency_id.id,
                'payment_date': self.payment_date,
                'journal_id': self.journal_id.id,
                'state': 'draft',
                'name': u'Efecto de Pago por medio de Letra : ' + self.num_letra
            }
            payment = self.env['account.payment'].create(data)
            payment.invoice_ids = invoice
            payment.post()

        if contador == len(letra.facturas_lineas_ids.ids):
            letra.state = 'charged'

    # def get_datos(self,letra_id):
    #     rec = {}
    #     letra = self.env['account.letra'].search([('id', '=',letra_id)], limit=1)
    #     if len(letra.ids) >= 1:
    #         rec['communication'] = letra['numerocorrelativo']
    #         rec['currency_id'] = letra['currency_id'].id
    #         rec['payment_type'] = letra['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
    #         rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[letra['type']]
    #         rec['partner_id'] = letra['partner_id'].id
    #         rec['amount'] = letra['monto_total']
    #         rec['state'] = 'draft'
    #
    #     return rec


    @api.model
    def default_get(self, fields):
        rec = self.default_get_origin(fields)
        #rec = [{'num_letra': }]
        letra = self.env['account.letra'].search([('id', '=', rec.get('num_letra'))], limit=1)
        if len(letra.ids) >= 1:
            rec['num_letra'] = letra['num_letra']
            rec['communication'] = letra['numerocorrelativo']
            rec['currency_id'] = letra['currency_id'].id
            rec['payment_type'] = letra['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[letra['type']]
            rec['partner_id'] = letra['partner_id'].id
            rec['amount'] = letra['monto_total']
            rec['state'] = 'draft'
        else:
            rec = super(AccountPayment, self).default_get(fields)
            invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
            if invoice_defaults and len(invoice_defaults) == 1:
                invoice = invoice_defaults[0]
                rec['communication'] = invoice['reference'] or invoice['name'] or invoice['number']
                rec['currency_id'] = invoice['currency_id'][0]
                rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
                rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
                rec['partner_id'] = invoice['partner_id'][0]
                rec['amount'] = invoice['residual']
        return rec
    # #
    # # def obtener_letra(self):
    # #     a=1
    # #
    def default_get_origin(self, fields_list):
        """ default_get(fields) -> default_values

        Return default values for the fields in ``fields_list``. Default
        values are determined by the context, user defaults, and the model
        itself.

        :param fields_list: a list of field names
        :return: a dictionary mapping each field name to its corresponding
            default value, if it has one.

        """
        # trigger view init hook
        self.view_init(fields_list)

        defaults = {}
        parent_fields = defaultdict(list)

        for name in fields_list:
            # 1. look up context
            key = 'default_' + name
            if key in self._context:
                defaults[name] = self._context[key]
                continue

            # 2. look up ir_values
            #    Note: performance is good, because get_defaults_dict is cached!
            ir_values_dict = self.env['ir.values'].get_defaults_dict(self._name)
            if name in ir_values_dict:
                defaults[name] = ir_values_dict[name]
                continue

            field = self._fields.get(name)

            # 3. look up field.default
            if field and field.default:
                defaults[name] = field.default(self)
                continue

            # 4. delegate to parent model
            if field and field.inherited:
                field = field.related_field
                parent_fields[field.model_name].append(field.name)

        # convert default values to the right format
        defaults = self._convert_to_write(defaults)

        # add default values for inherited fields
        for model, names in parent_fields.iteritems():
            defaults.update(self.env[model].default_get(names))

        return defaults
