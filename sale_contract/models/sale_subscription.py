# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _description = "Sale Subscription"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _inherit = 'mail.thread'

    state = fields.Selection([('draft', 'New'), ('open', 'In Progress'), ('pending', 'To Renew'),
                              ('close', 'Closed'), ('cancel', 'Cancelled')],
                             string='Status', required=True, track_visibility='onchange', copy=False, default='draft')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True, ondelete="cascade", auto_join=True)
    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date = fields.Date(string='End Date', track_visibility='onchange', help="If set in advance, the subscription will be set to pending 1 month before the date and will be closed on the date set in this field.")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True)
    currency_id = fields.Many2one('res.currency', related='pricelist_id.currency_id', string='Currency', readonly=True)
    recurring_invoice_line_ids = fields.One2many('sale.subscription.line', 'analytic_account_id', string='Invoice Lines', copy=True)
    recurring_rule_type = fields.Selection(string='Recurrence', help="Invoice automatically repeat at specified interval", related="template_id.recurring_rule_type", readonly=1)
    recurring_interval = fields.Integer(string='Repeat Every', help="Repeat every (Days/Week/Month/Year)", related="template_id.recurring_interval", readonly=1)
    recurring_next_date = fields.Date(string='Date of Next Invoice', default=fields.Date.today, help="The next invoice will be created on this date then the period will be extended.")
    recurring_total = fields.Float(compute='_compute_recurring_total', string="Recurring Price", store=True, track_visibility='onchange')
    close_reason_id = fields.Many2one("sale.subscription.close.reason", string="Close Reason", track_visibility='onchange')
    template_id = fields.Many2one('sale.subscription.template', string='Subscription Template', required=True, track_visibility='onchange')
    description = fields.Text()
    user_id = fields.Many2one('res.users', string='Sales Rep', track_visibility='onchange')
    invoice_count = fields.Integer(compute='_compute_invoice_count')

    @api.model
    def default_get(self, fields):
        defaults = super(SaleSubscription, self).default_get(fields)
        if 'code' in fields:
            defaults.update(code=self.env['ir.sequence'].next_by_code('sale.subscription') or 'New')
        return defaults

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values:
            return 'sale_contract.subtype_state_change'
        return super(SaleSubscription, self)._track_subtype(init_values)

    def _compute_invoice_count(self):
        orders = self.env['sale.order'].search_read(domain=[('subscription_id', 'in', self.ids)], fields=['name'])
        order_names = [order['name'] for order in orders]
        invoice_line_data = self.env['account.invoice.line'].read_group(
            domain=[('account_analytic_id', 'in', self.mapped('analytic_account_id').ids),
                    ('invoice_id.origin', 'in', self.mapped('code') + order_names),
                    ('invoice_id.state', 'in', ['draft', 'open', 'paid'])],
            fields=["account_analytic_id", "invoice_id"],
            groupby=["account_analytic_id", "invoice_id"],
            lazy=False)
        for sub in self:
            sub.invoice_count = len(filter(lambda d: d['account_analytic_id'][0] == sub.analytic_account_id.id, invoice_line_data))

    @api.depends('recurring_invoice_line_ids', 'recurring_invoice_line_ids.quantity', 'recurring_invoice_line_ids.price_subtotal')
    def _compute_recurring_total(self):
        for account in self:
            account.recurring_total = sum(line.price_subtotal for line in account.recurring_invoice_line_ids)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist.id
        if self.partner_id.user_id:
            self.user_id = self.partner_id.user_id

    @api.onchange('template_id')
    def on_change_template(self):
        if self.template_id:
            # Check if record is a new record or exists in db by checking its _origin
            # note that this property is not always set, hence the getattr
            if not getattr(self, '_origin', self.browse()) and not isinstance(self.id, int):
                invoice_line_ids = []
                for line in self.template_id.subscription_template_line_ids:
                    product = line.product_id.with_context(
                        lang=self.partner_id.lang,
                        partner=self.partner_id.id,
                        pricelist=self.pricelist_id.id,
                        uom=line.uom_id.id
                    )
                    name = product.name_get()[0][1]
                    if product.description_sale:
                        name += '\n' + product.description_sale
                    invoice_line_ids.append((0, 0, {
                        'product_id': line.product_id.id,
                        'uom_id': line.uom_id.id,
                        'name': line.name,
                        'actual_quantity': line.quantity,
                        'price_unit': product.price,
                    }))
                self.recurring_invoice_line_ids = invoice_line_ids
                self.description = self.template_id.description
            self.recurring_interval = self.template_id.recurring_interval
            self.recurring_rule_type = self.template_id.recurring_rule_type

    @api.model
    def create(self, vals):
        vals['code'] = (
            vals.get('code') or
            self.env.context.get('default_code') or
            self.env['ir.sequence'].with_context(force_company=vals.get('company_id')).next_by_code('sale.subscription') or
            'New'
        )
        if vals.get('name', 'New') == 'New' and not vals.get('analytic_account_id'):
            vals['name'] = vals['code']
        return super(SaleSubscription, self).create(vals)

    @api.multi
    def name_get(self):
        res = []
        for sub in self:
            name = '%s - %s' % (sub.code, sub.partner_id.name) if sub.code else sub.partner_id.name
            res.append((sub.id, '%s/%s' % (sub.template_id.code, name) if sub.template_id.code else name))
        return res

    @api.multi
    def action_subscription_invoice(self):
        analytic_ids = [sub.analytic_account_id.id for sub in self]
        orders = self.env['sale.order'].search_read(domain=[('subscription_id', 'in', self.ids)], fields=['name'])
        order_names = [order['name'] for order in orders]
        invoices = self.env['account.invoice'].search([('invoice_line_ids.account_analytic_id', 'in', analytic_ids),
                                                       ('origin', 'in', self.mapped('code') + order_names)])
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "views": [[self.env.ref('account.invoice_tree').id, "tree"],
                      [self.env.ref('account.invoice_form').id, "form"]],
            "domain": [["id", "in", invoices.ids]],
            "context": {"create": False},
            "name": "Invoices",
        }

    @api.model
    def cron_account_analytic_account(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to pending if date is in less than a month
        domain_pending = [('date', '<', next_month), ('state', '=', 'open')]
        subscriptions_pending = self.search(domain_pending)
        subscriptions_pending.write({'state': 'pending'})

        # set to close if data is passed
        domain_close = [('date', '<', today), ('state', 'in', ['pending', 'open'])]
        subscriptions_close = self.search(domain_close)
        subscriptions_close.write({'state': 'close'})

        return dict(pending=subscriptions_pending.ids, closed=subscriptions_close.ids)

    @api.model
    def _cron_recurring_create_invoice(self):
        return self._recurring_create_invoice(automatic=True)

    @api.multi
    def set_open(self):
        return self.write({'state': 'open', 'date': False})

    @api.multi
    def set_pending(self):
        return self.write({'state': 'pending'})

    @api.multi
    def set_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def set_close(self):
        return self.write({'state': 'close', 'date': fields.Date.from_string(fields.Date.today())})

    @api.multi
    def _prepare_invoice_data(self):
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_("You must first select a Customer for Subscription %s!") % self.name)

        if 'force_company' in self.env.context:
            company = self.env['res.company'].browse(self.env.context['force_company'])
        else:
            company = self.company_id
            self = self.with_context(force_company=company.id, company_id=company.id)

        fpos_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id)
        journal = self.template_id.journal_id or self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
        if not journal:
            raise UserError(_('Please define a sale journal for the company "%s".') % (company.name or '', ))

        next_date = fields.Date.from_string(self.recurring_next_date)
        if not next_date:
            raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.display_name,))
        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        end_date = next_date + relativedelta(**{periods[self.recurring_rule_type]: self.recurring_interval})
        end_date = end_date - relativedelta(days=1)     # remove 1 day as normal people thinks in term of inclusive ranges.
        # DO NOT FORWARDPORT
        format_date = self.env['ir.qweb.field.date'].value_to_html
        addr = self.partner_id.address_get(['delivery'])

        return {
            'account_id': self.partner_id.property_account_receivable_id.id,
            'type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'partner_shipping_id': addr['delivery'],
            'currency_id': self.pricelist_id.currency_id.id,
            'journal_id': journal.id,
            'origin': self.code,
            'fiscal_position_id': fpos_id,
            'payment_term_id': self.partner_id.property_payment_term_id.id,
            'company_id': company.id,
            'comment': _("This invoice covers the following period: %s - %s") % (format_date(fields.Date.to_string(next_date), {}), format_date(fields.Date.to_string(end_date), {})),
            'user_id': self.user_id.id,
        }

    @api.multi
    def _prepare_invoice_line(self, line, fiscal_position):
        if 'force_company' in self.env.context:
            company = self.env['res.company'].browse(self.env.context['force_company'])
        else:
            company = line.analytic_account_id.company_id
            line = line.with_context(force_company=company.id, company_id=company.id)

        account = line.product_id.property_account_income_id
        if not account:
            account = line.product_id.categ_id.property_account_income_categ_id
        account_id = fiscal_position.map_account(account).id

        tax = line.product_id.taxes_id.filtered(lambda r: r.company_id == company)
        tax = fiscal_position.map_tax(tax, product=line.product_id, partner=self.partner_id)
        return {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': line.analytic_account_id.analytic_account_id.id,
            'price_unit': line.price_unit or 0.0,
            'discount': line.discount,
            'quantity': line.quantity,
            'uom_id': line.uom_id.id,
            'product_id': line.product_id.id,
            'invoice_line_tax_ids': [(6, 0, tax.ids)],
        }

    @api.multi
    def _prepare_invoice_lines(self, fiscal_position):
        self.ensure_one()
        fiscal_position = self.env['account.fiscal.position'].browse(fiscal_position)
        return [(0, 0, self._prepare_invoice_line(line, fiscal_position)) for line in self.recurring_invoice_line_ids]

    @api.multi
    def _prepare_invoice(self):
        invoice = self._prepare_invoice_data()
        invoice['invoice_line_ids'] = self._prepare_invoice_lines(invoice['fiscal_position_id'])
        return invoice

    @api.multi
    def recurring_invoice(self):
        self._recurring_create_invoice()
        return self.action_subscription_invoice()

    @api.returns('account.invoice')
    def _recurring_create_invoice(self, automatic=False):
        auto_commit = self.env.context.get('auto_commit', True)
        AccountInvoice = self.env['account.invoice']
        invoices = []
        current_date = fields.Date.today()
        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        domain = [('id', 'in', self.ids)] if self.ids else [('recurring_next_date', '<=', current_date), ('state', '=', 'open')]
        sub_data = self.search_read(fields=['id', 'company_id'], domain=domain)
        for company_id in set(data['company_id'][0] for data in sub_data):
            sub_ids = map(lambda s: s['id'], filter(lambda s: s['company_id'][0] == company_id, sub_data))
            subs = self.with_context(company_id=company_id, force_company=company_id).browse(sub_ids)
            for sub in subs:
                try:
                    invoices.append(AccountInvoice.create(sub._prepare_invoice()))
                    invoices[-1].message_post_with_view('mail.message_origin_link',
                     values={'self': invoices[-1], 'origin': sub},
                     subtype_id=self.env.ref('mail.mt_note').id)
                    invoices[-1].compute_taxes()
                    next_date = fields.Date.from_string(sub.recurring_next_date or current_date)
                    rule, interval = sub.recurring_rule_type, sub.recurring_interval
                    new_date = next_date + relativedelta(**{periods[rule]: interval})
                    sub.write({'recurring_next_date': new_date})
                    if automatic and auto_commit:
                        self.env.cr.commit()
                except Exception:
                    if automatic and auto_commit:
                        self.env.cr.rollback()
                        _logger.exception('Fail to create recurring invoice for subscription %s', sub.code)
                    else:
                        raise
        return invoices

    @api.multi
    def _prepare_renewal_order_values(self):
        res = dict()
        for contract in self:
            order_lines = []
            fpos_id = self.env['account.fiscal.position'].get_fiscal_position(contract.partner_id.id)
            for line in contract.recurring_invoice_line_ids:
                order_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.product_tmpl_id.name,
                    'product_uom': line.uom_id.id,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'name': line.name,
                }))
            addr = contract.partner_id.address_get(['delivery', 'invoice'])
            res[contract.id] = {
                'pricelist_id': contract.pricelist_id.id,
                'partner_id': contract.partner_id.id,
                'partner_invoice_id': addr['invoice'],
                'partner_shipping_id': addr['delivery'],
                'currency_id': contract.pricelist_id.currency_id.id,
                'order_line': order_lines,
                'project_id': contract.analytic_account_id.id,
                'subscription_management': 'renew',
                'note': contract.description,
                'fiscal_position_id': fpos_id,
                'user_id': contract.user_id.id,
                'payment_term_id': contract.partner_id.property_payment_term_id.id,
            }
        return res

    @api.multi
    def prepare_renewal_order(self):
        self.ensure_one()
        values = self._prepare_renewal_order_values()
        order = self.env['sale.order'].create(values[self.id])
        order.order_line._compute_tax_id()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": order.id,
        }

    @api.multi
    def increment_period(self):
        for account in self:
            current_date = account.recurring_next_date or self.default_get(['recurring_next_date'])['recurring_next_date']
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            new_date = fields.Date.from_string(current_date) + relativedelta(**{periods[account.recurring_rule_type]: account.recurring_interval})
            account.write({'recurring_next_date': new_date})

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('code', operator, name), ('name', operator, name)]
        partners = self.env['res.partner'].search([('name', operator, name)], limit=limit)
        if partners:
            domain = ['|'] + domain + [('partner_id', 'in', partners.ids)]
        rec = self.search(domain + args, limit=limit)
        return rec.name_get()


class SaleSubscriptionLine(models.Model):
    _name = "sale.subscription.line"
    _description = "Susbcription Line"

    product_id = fields.Many2one('product.product', string='Product', domain="[('recurring_invoice','=',True)]", required=True)
    analytic_account_id = fields.Many2one('sale.subscription', string='Subscription')
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(compute='_compute_quantity', inverse='_set_quantity', string='Quantity', store=True,
                            digits=dp.get_precision('Product Unit of Measure'),
                            help="Max between actual and sold quantities; this quantity will be invoiced")
    actual_quantity = fields.Float(help="Quantity actually used by the customer", default=0.0, digits=dp.get_precision('Product Unit of Measure'))
    sold_quantity = fields.Float(help="Quantity sold to the customer", required=True, default=1, digits=dp.get_precision('Product Unit of Measure'))
    uom_id = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'))
    price_subtotal = fields.Float(compute='_compute_price_subtotal', string='Sub Total', digits=dp.get_precision('Account'))

    @api.depends('sold_quantity', 'actual_quantity')
    def _compute_quantity(self):
        for line in self:
            line.quantity = max(line.sold_quantity, line.actual_quantity)

    @api.multi
    def _set_quantity(self):
        for line in self:
            line.actual_quantity = line.quantity

    @api.depends('price_unit', 'quantity', 'discount', 'analytic_account_id.pricelist_id')
    def _compute_price_subtotal(self):
        for line in self:
            line_sudo = line.sudo()
            price = line.env['account.tax']._fix_tax_included_price(line.price_unit, line_sudo.product_id.taxes_id, [])
            line.price_subtotal = line.quantity * price * (100.0 - line.discount) / 100.0
            if line.analytic_account_id.pricelist_id:
                line.price_subtotal = line_sudo.analytic_account_id.pricelist_id.currency_id.round(line.price_subtotal)

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id
        partner = self.analytic_account_id.partner_id
        if partner.lang:
            self.product_id.with_context(lang=partner.lang)

        name = product.display_name
        if product.description_sale:
            name += '\n' + product.description_sale
        self.name = name

    @api.onchange('product_id', 'quantity')
    def onchange_product_quantity(self):
        domain = {}
        contract = self.analytic_account_id
        company_id = contract.company_id.id
        pricelist_id = contract.pricelist_id.id
        context = dict(self.env.context, company_id=company_id, force_company=company_id, pricelist=pricelist_id, quantity=self.quantity)
        if not self.product_id:
            self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            partner = contract.partner_id.with_context(context)
            if partner.lang:
                context.update({'lang': partner.lang})

            product = self.product_id.with_context(context)
            self.price_unit = product.price

            if not self.uom_id:
                self.uom_id = product.uom_id.id
            if self.uom_id.id != product.uom_id.id:
                self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

        return {'domain': domain}

    @api.onchange('uom_id')
    def onchange_uom_id(self):
        if not self.uom_id:
            self.price_unit = 0.0
        else:
            self.onchange_product_id()


class SaleSubscriptionCloseReason(models.Model):
    _name = "sale.subscription.close.reason"
    _order = "sequence, id"
    _description = "Susbcription Close Reason"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)


class SaleSubscriptionTemplate(models.Model):
    _name = "sale.subscription.template"
    _description = "Sale Subscription Template"
    _inherit = "mail.thread"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    code = fields.Char()
    description = fields.Text(translate=True)
    recurring_rule_type = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'),
                                            ('monthly', 'Month(s)'), ('yearly', 'Year(s)'), ],
                                           string='Recurrence',
                                           help="Invoice automatically repeat at specified interval",
                                           default='monthly')
    recurring_interval = fields.Integer(string="Repeat Every", help="Repeat every (Days/Week/Month/Year)", default=1, track_visibility='onchange')
    subscription_template_line_ids = fields.One2many('sale.subscription.template.line', 'subscription_template_id', string="Subscription Template Lines", copy=True)
    journal_id = fields.Many2one('account.journal', string="Accounting Journal", domain="[('type', '=', 'sale')]", company_dependent=True,
                                 help="If set, subscriptions with this template will invoice in this journal; "
                                      "otherwise the sales journal with the lowest sequence is used.")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # positive and negative operators behave differently
        if operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        else:
            domain = ['&', ('code', operator, name), ('name', operator, name)]
        args = args or []
        rec = self.search(domain + args, limit=limit)
        return rec.name_get()

    @api.multi
    def name_get(self):
        res = []
        for sub in self:
            name = '%s - %s' % (sub.code, sub.name) if sub.code else sub.name
            res.append((sub.id, name))
        return res


class SaleSubscriptionTemplateLine(models.Model):
    _name = "sale.subscription.template.line"
    _description = "Subscription Template Line"

    product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('recurring_invoice', '=', True)]")
    name = fields.Char(string='Description', required=True)
    subscription_template_id = fields.Many2one('sale.subscription.template', string="Template", required=True, ondelete="cascade")
    uom_id = fields.Many2one('product.uom', string="Unit of Measure", required=True)
    quantity = fields.Float(required=True, default=1.0)
    price = fields.Float(compute='_compute_price')

    @api.onchange('product_id')
    def onchange_product_id(self):
        domain = {}
        if not self.product_id:
            domain['uom_id'] = []
        else:
            name = self.product_id.display_name
            if self.product_id.description_sale:
                name += '\n' + self.product_id.description_sale
            self.name = name

            if not self.uom_id:
                self.uom_id = self.product_id.uom_id.id
            domain['uom_id'] = [('category_id', '=', self.product_id.uom_id.category_id.id)]

        return {'domain': domain}

    def _compute_price(self):
        pricelist = self.env['product.pricelist'].browse(self._context.get('pricelist_id'))
        for line in self:
            if not pricelist:
                line.price = 0.0
            else:
                line.price = pricelist.with_context(uom=line.uom_id.id).price_get(line.product_id.id, line.quantity)[pricelist.id]
