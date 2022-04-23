# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import pdb
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from datetime import datetime, timedelta,date

from odoo.exceptions import Warning
from odoo.exceptions import UserError
from json import dumps

import json
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import json
import re

from odoo.addons.sale_timesheet_enterprise.models.sale import DEFAULT_INVOICED_TIMESHEET

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    custom_timesheet_invoice_id = fields.Many2one('account.move', string="Custom Invoices", readonly=True, copy=False, help="Invoice created from the timesheet")


class AccountMove(models.Model):
    _inherit= 'account.move'

    delivery_site = fields.Many2one('delivery.sites',string='Delivery site')
    # delivery_site = fields.Selection([('onsite','On Site'),('offsite','Off Site')],string='Delivery site')
    service_period_from = fields.Date(string='Service Period From',store=True,track_visibility='always',compute='compute_from')
    service_period_to = fields.Date(string='Service Period To',store=True,track_visibility='always',compute='compute_to')
    resource_name = fields.Many2one('hr.employee',string='Resource Name',store=True,track_visibility='always',compute='compute_resource')
    service_period = fields.Char(compute='_get_service_period',store=True)

    @api.depends('invoice_line_ids.service_period_from')
    def _get_service_period(self):
        for rec in self:
            if rec.type in ['out_invoice']:
                for line in rec.invoice_line_ids:
                    if line.service_period_from:
                        rec.service_period = line.service_period_from.strftime("%B-%Y")
                    else:
                        rec.service_period = False



    @api.depends('invoice_line_ids.resource_name')
    def compute_resource(self):
        for l in self:
            l.resource_name = False
            for line in l.invoice_line_ids:
                if line.resource_name:
                    l.resource_name = line.resource_name
                else:
                    l.resource_name = False

    @api.depends('invoice_line_ids.service_period_from')
    def compute_from(self):
        for l in self:
            l.service_period_from = False
            for line in l.invoice_line_ids:
                if line.service_period_from:
                    l.service_period_from = line.service_period_from
                else:
                    l.service_period_from = False

    @api.depends('invoice_line_ids.service_period_to')
    def compute_to(self):
        for l in self:
            l.service_period_to = False
            for line in l.invoice_line_ids:
                if line.service_period_to:
                    l.service_period_to = line.service_period_to
                else:
                    l.service_period_to = False


    #custom timesheets
    custom_timesheet_ids = fields.One2many('account.analytic.line', 'custom_timesheet_invoice_id', string=' Custom Timesheets', readonly=True, copy=False)
    custom_timesheet_count = fields.Integer("Number of  custom timesheets", compute='_compute_custom_timesheet_count')

    @api.depends('custom_timesheet_ids')
    def _compute_custom_timesheet_count(self):
        timesheet_data = self.env['account.analytic.line'].read_group([('custom_timesheet_invoice_id', 'in', self.ids)], ['custom_timesheet_invoice_id'], ['custom_timesheet_invoice_id'])
        mapped_data = dict([(t['custom_timesheet_invoice_id'][0], t['custom_timesheet_invoice_id_count']) for t in timesheet_data])
        for invoice in self:
            invoice.custom_timesheet_count = mapped_data.get(invoice.id, 0)

    def action_view_custom_timesheet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Timesheets'),
            'domain': [('project_id', '!=', False)],
            'res_model': 'account.analytic.line',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _("""
                <p class="o_view_nocontent_smiling_face">
                    Record timesheets
                </p><p>
                    You can register and track your workings hours by project every
                    day. Every time spent on a project will become a cost and can be re-invoiced to
                    customers if required.
                </p>
            """),
            'limit': 80,
            'context': {
                'default_project_id': self.id,
                'search_default_project_id': [self.id]
            }
        }






class AccountMoveLine(models.Model):
    _inherit= 'account.move.line'

    per_day = fields.Float(string='Per Day',store=True)
    price_in = fields.Float(string='Price unit',store=True,track_visibility='always',compute='Onchange_price')
    service_period_from = fields.Date(string='Service Period From')
    service_period_to = fields.Date(string='Service Period To')
    resource_name = fields.Many2one('hr.employee',string='Resource Name')
    uom_name = fields.Char(compute='get_uom_name', store=True)


    @api.depends('product_uom_id')
    def get_uom_name(self):
        for line in self:
            if line.product_uom_id:
                line.uom_name = line.product_uom_id.name
            else:
                line.uom_name = None




    @api.onchange('product_uom_id')
    def Onchange_days(self):
        # self.check_perday = False
        # print(self.check_perday,'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAS')
        for line in self:
            if line.move_id.type in ['out_invoice','out_refund']:
                if not line.product_uom_id.name in ['Hours','Month']:
                    # if line.price_unit != 0:
                    line.per_day = line.price_unit / line.product_uom_id.factor_inv
                    # else:
                    #     line.per_day = 0.0
                else:
                    line.per_day = 0.0

    @api.depends('price_unit')
    def Onchange_price(self):
        for l in self:
            if l.move_id.type in ['out_invoice','out_refund']:
                if l.price_unit:
                    l.price_in = l.price_unit
                else:
                    l.price_in = 0.0
            else:
                l.price_in = 0.0


    # @api.model
    # def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency,product, partner, taxes, move_type):
    #     ''' This method is used to compute 'price_total' & 'price_subtotal'.

    #     :param price_unit:  The current price unit.
    #     :param quantity:    The current quantity.
    #     :param discount:    The current discount.
    #     :param currency:    The line's currency.
    #     :param product:     The line's product.
    #     :param partner:     The line's partner.
    #     :param taxes:       The applied taxes.
    #     :param move_type:   The type of the move.
    #     :return:            A dictionary containing 'price_subtotal' & 'price_total'.
    #     '''
    #     res = {}

    #     # Compute 'price_subtotal'.
    #     if self.per_day == 0.0:
    #         price_unit_wo_discount = price_unit * (1 - (discount / 100.0))
    #         subtotal = quantity * price_unit_wo_discount

    #         # Compute 'price_total'.
    #         if taxes:
    #             taxes_res = taxes._origin.compute_all(price_unit_wo_discount,
    #                 quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
    #             res['price_subtotal'] = taxes_res['total_excluded']
    #             res['price_total'] = taxes_res['total_included']
    #         else:
    #             res['price_total'] = res['price_subtotal'] = subtotal
    #         return res
    #     else:
    #         price_unit_wo_discount = self.per_day * (1 - (discount / 100.0))
    #         subtotal = quantity * price_unit_wo_discount

    #         # Compute 'price_total'.
    #         if taxes:
    #             taxes_res = taxes._origin.compute_all(price_unit_wo_discount,
    #                 quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
    #             res['price_subtotal'] = taxes_res['total_excluded']
    #             res['price_total'] = taxes_res['total_included']
    #         else:
    #             res['price_total'] = res['price_subtotal'] = subtotal
    #         return res


    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        lines_to_process_custom = res.filtered(lambda line: line.move_id.type == 'out_invoice' and line.move_id.state == 'draft')

        for line in lines_to_process_custom:
            sale_line_delivery_custom = line.sale_line_ids.filtered(lambda sol: sol.product_id.invoice_policy == 'delivery' and sol.product_id.service_type == 'timesheet')
            moveid = line.move_id
            if sale_line_delivery_custom:
                if moveid.delivery_site:
                    domain = [
                        '&',
                        '&',
                        ('so_line', 'in', sale_line_delivery_custom.ids),
                        ('delivery_site','=',moveid.delivery_site.id),
                        '&',
                        ('custom_timesheet_invoice_id', '=', False),
                        ('project_id', '!=', False)
                    ]
                else:
                    domain = [
                        '&',
                        ('so_line', 'in', sale_line_delivery_custom.ids),
                        '&',
                        ('custom_timesheet_invoice_id', '=', False),
                        ('project_id', '!=', False)
                    ]
                # domain = expression.AND([[('delivery_site', '=', moveid.delivery_site),('delivery_site','!=', None)],domain])
                param_invoiced_timesheet = self.env['ir.config_parameter'].sudo().get_param('sale.invoiced_timesheet', DEFAULT_INVOICED_TIMESHEET)
                if param_invoiced_timesheet == 'approved':
                    domain = expression.AND([domain, [('validated', '=', True)]])
                timesheets = self.env['account.analytic.line'].search(domain).sudo()
                timesheets.write({
                    'custom_timesheet_invoice_id': line.move_id.id,
                })
                
                        
        return res








class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    # site = fields.Selection([
    #     ('onsite','On Site'),
    #     ('offsite','Off Site')
    #     ], string='Create OnSite or OffSite Invoice',
    #     help="A standard invoice is issued with all the order lines ready for invoicing, \
    #     according to their invoicing policy (based on ordered or delivered quantity).")
    site = fields.Many2one('delivery.sites', string='Create OnSite or OffSite Invoice',
        help="A standard invoice is issued with all the order lines ready for invoicing, \
        according to their invoicing policy (based on ordered or delivered quantity).")


    def _create_invoice(self, order, so_line, amount):
        if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.fixed_amount
            name = _('Down Payment')
        if self.advance_payment_method == 'delivered' and self.site.id == 1:
            invoice_vals = {
                'type': 'out_invoice',
                'invoice_origin': order.name,
                'invoice_user_id': order.user_id.id,
                'narration': order.note,
                'partner_id': order.partner_invoice_id.id,
                'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
                'partner_shipping_id': order.partner_shipping_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                'invoice_payment_ref': order.client_order_ref,
                'invoice_payment_term_id': order.payment_term_id.id,
                'invoice_partner_bank_id': order.company_id.partner_id.bank_ids[:1],
                'team_id': order.team_id.id,
                'campaign_id': order.campaign_id.id,
                'medium_id': order.medium_id.id,
                'source_id': order.source_id.id,
                'delivery_site':1,
                'invoice_line_ids': [(0, 0, {
                    'name': name,
                    'price_unit':False,
                    'quantity': 0.0,
                    'product_id': self.product_id.id,
                    'product_uom_id': so_line.product_uom.id,
                    'tax_ids': [(6, 0, so_line.tax_id.ids)],
                    'sale_line_ids': [(6, 0, [so_line.id])],
                    'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                    'analytic_account_id': order.analytic_account_id.id or False,
                })],
            }
            if order.fiscal_position_id:
                invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
            invoice = self.env['account.move'].create(invoice_vals)
            invoice.message_post_with_view('mail.message_origin_link',
                        values={'self': invoice, 'origin': order},
                        subtype_id=self.env.ref('mail.mt_note').id)
            return invoice
        elif self.advance_payment_method == 'delivered' and self.site.id == 2:
            invoice_vals = {
                'type': 'out_invoice',
                'invoice_origin': order.name,
                'invoice_user_id': order.user_id.id,
                'narration': order.note,
                'partner_id': order.partner_invoice_id.id,
                'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
                'partner_shipping_id': order.partner_shipping_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                'invoice_payment_ref': order.client_order_ref,
                'invoice_payment_term_id': order.payment_term_id.id,
                'invoice_partner_bank_id': order.company_id.partner_id.bank_ids[:1],
                'team_id': order.team_id.id,
                'campaign_id': order.campaign_id.id,
                'medium_id': order.medium_id.id,
                'source_id': order.source_id.id,
                'delivery_site':2,
                'invoice_line_ids': [(0, 0, {
                    'name': name,
                    'price_unit':False,
                    'quantity': 0.0,
                    'product_id': self.product_id.id,
                    'product_uom_id': so_line.product_uom.id,
                    'tax_ids': [(6, 0, so_line.tax_id.ids)],
                    'sale_line_ids': [(6, 0, [so_line.id])],
                    'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                    'analytic_account_id': order.analytic_account_id.id or False,
                })],
            }
            if order.fiscal_position_id:
                invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
            invoice = self.env['account.move'].create(invoice_vals)
            invoice.message_post_with_view('mail.message_origin_link',
                        values={'self': invoice, 'origin': order},
                        subtype_id=self.env.ref('mail.mt_note').id)
            return invoice
        else:
            invoice_vals = {
            'type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'invoice_payment_ref': order.client_order_ref,
            'invoice_payment_term_id': order.payment_term_id.id,
            'invoice_partner_bank_id': order.company_id.partner_id.bank_ids[:1],
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }
        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice


    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            sale_orders.write({'salesite':self.site.id})
            sale_orders._create_invoices(final=self.deduct_down_payments) 
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.fixed_amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
                so_line = sale_line_obj.create({
                    'name': _('Down Payment: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'analytic_tag_ids': analytic_tag_ids,
                    'tax_id': [(6, 0, tax_ids)],
                    'is_downpayment': True,
                })
                del context
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}




