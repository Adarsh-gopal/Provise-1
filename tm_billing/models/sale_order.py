from odoo import api, fields, models, _
import pdb
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



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # salesite = fields.Selection([
    #     ('onsite','On Site'),
    #     ('offsite','Off Site')
    #     ], string='Create On Site or Off Site Invoice')
    salesite = fields.Many2one('delivery.sites', string='Create On Site or Off Site Invoice')
    balance = fields.Float(string='Balance')

    sale_payment_widget = fields.Text(compute='_compute_payments_info')

    amount_due = fields.Monetary(compute='get_balance_amount')



    def get_balance_amount(self):
        for rec in self: 
            invoices = self.env['account.move'].search([('invoice_origin','=',rec.name),('state','=','posted')])
            total_paid = 0.0
            for each_inv in invoices:
                if each_inv.state == 'posted':
                    print('**************', each_inv.amount_total)
                    total_paid = total_paid + each_inv.amount_total

            rec.amount_due = rec.amount_total - total_paid


            # invoice_line = self.env['account.move'].search([('invoice_origin','=',rec.name),('state','=','posted')])
            # for line in invoice_line:
            #     print('*******************',line.amount_total,line.name,total_paid)
            # print(rec.amount_total,'*************************',total_paid)

            # rec.amount_due = rec.amount_total - total_paid


    def _get_reconciled_info_JSON_values(self):
        self.ensure_one()
        payment_vals = []
        for rec in self:
            invoice_line = self.env['account.move'].search([('invoice_origin','=',rec.name),('state','=','posted')])
            for lines in invoice_line:
                payment_vals.append({
                    'posting_date': lines.invoice_date,
                    'posting_amount': lines.amount_total,
                    'currency':lines.currency_id.symbol,
                    'position': lines.currency_id.position,
                    'invoice_ref':lines.name,
                    'delivery_site':lines.delivery_site.name,
                    'service_period':lines.service_period,

                })
        return payment_vals

    def _compute_payments_info(self):
        for rec in self:            
            payment_vals = rec._get_reconciled_info_JSON_values()
            if payment_vals:
                info = {
                    'content': payment_vals,
                }
                rec.sale_payment_widget = json.dumps(info, default=date_utils.json_default)
            else:
                rec.sale_payment_widget = json.dumps(False)



    def _prepare_invoice(self):
        self.ensure_one()
        journal = self.env['account.move'].with_context(force_company=self.company_id.id, default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        var = self.env['sale.advance.payment.inv'].search([('advance_payment_method','=','delivered'),('site','=',1),('site','=',self.salesite.id)])
        if var:
            invoice_vals = {
                'ref': self.client_order_ref or '',
                'type': 'out_invoice',
                'narration': self.note,
                'currency_id': self.currency_id.id,
                'campaign_id': self.campaign_id.id,
                'medium_id': self.medium_id.id,
                'source_id': self.source_id.id,
                'invoice_user_id': self.user_id and self.user_id.id,
                'team_id': self.team_id.id,
                'partner_id': self.partner_invoice_id.id,
                'partner_shipping_id': self.partner_shipping_id.id,
                'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
                'invoice_origin': self.name,
                'invoice_payment_term_id': self.payment_term_id.id,
                'invoice_payment_ref': self.reference,
                'delivery_site':1,
                'transaction_ids': [(6, 0, self.transaction_ids.ids)],
                'invoice_line_ids': [],
                
            }
            return invoice_vals
        elif self.env['sale.advance.payment.inv'].search([('advance_payment_method','=','delivered'),('site','=',2),('site','=',self.salesite.id)]):
            invoice_vals = {
                'ref': self.client_order_ref or '',
                'type': 'out_invoice',
                'narration': self.note,
                'currency_id': self.currency_id.id,
                'campaign_id': self.campaign_id.id,
                'medium_id': self.medium_id.id,
                'source_id': self.source_id.id,
                'invoice_user_id': self.user_id and self.user_id.id,
                'team_id': self.team_id.id,
                'partner_id': self.partner_invoice_id.id,
                'partner_shipping_id': self.partner_shipping_id.id,
                'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
                'invoice_origin': self.name,
                'invoice_payment_term_id': self.payment_term_id.id,
                'invoice_payment_ref': self.reference,
                'delivery_site':2,
                'transaction_ids': [(6, 0, self.transaction_ids.ids)],
                'invoice_line_ids': [],
                
            }
            return invoice_vals
        else:
            invoice_vals = {
                'ref': self.client_order_ref or '',
                'type': 'out_invoice',
                'narration': self.note,
                'currency_id': self.currency_id.id,
                'campaign_id': self.campaign_id.id,
                'medium_id': self.medium_id.id,
                'source_id': self.source_id.id,
                'invoice_user_id': self.user_id and self.user_id.id,
                'team_id': self.team_id.id,
                'partner_id': self.partner_invoice_id.id,
                'partner_shipping_id': self.partner_shipping_id.id,
                'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
                'invoice_origin': self.name,
                'invoice_payment_term_id': self.payment_term_id.id,
                'invoice_payment_ref': self.reference,
                'transaction_ids': [(6, 0, self.transaction_ids.ids)],
                'invoice_line_ids': [],
                
            }
            return invoice_vals

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # s_date = fields.Date(string='Date')

    # @api.onchange('s_date')
    # def onchange_date(self):
    #     if self.s_date == self.s_date:
    #         print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    #         raise Warning('Please select a date equal/or greater than the current date')

    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        price = 0
        if self.env['sale.advance.payment.inv'].search([('advance_payment_method','=','delivered'),('site','=',2),('site','=',self.order_id.salesite.id)]) or self.env['sale.advance.payment.inv'].search([('advance_payment_method','=','delivered'),('site','=',2),('site','=',self.order_id.salesite.id)]):
            if not self.product_uom.name in ['Month','Hours']:
                price = (self.price_unit / self.product_uom.factor_inv)
                return {
                    'display_type': self.display_type,
                    'sequence': self.sequence,
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'resource_name': self.resource_name.id,
                    'quantity': False,
                    'discount': False,
                    'price_unit': self.price_unit,
                    'product_uom_id': self.product_uom.id,
                    'per_day': price,
                    'tax_ids': [(6, 0, self.tax_id.ids)],
                    'analytic_account_id': self.order_id.analytic_account_id.id,
                    'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                    'sale_line_ids': [(4, self.id)],
                }
            else:
                return {
                    'display_type': self.display_type,
                    'sequence': self.sequence,
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'resource_name': self.resource_name.id,
                    'quantity': False,
                    'discount': False,
                    'price_unit': self.price_unit,
                    'product_uom_id': self.product_uom.id,
                    'tax_ids': [(6, 0, self.tax_id.ids)],
                    'analytic_account_id': self.order_id.analytic_account_id.id,
                    'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                    'sale_line_ids': [(4, self.id)],
                }

        else:
            return {
                'display_type': self.display_type,
                'sequence': self.sequence,
                'name': self.name,
                'product_id': self.product_id.id,
                'resource_name': self.resource_name.id,
                'product_uom_id': self.product_uom.id,
                'quantity': self.qty_to_invoice,
                'discount': self.discount,
                'price_unit': self.price_unit,
                'tax_ids': [(6, 0, self.tax_id.ids)],
                'analytic_account_id': self.order_id.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                'sale_line_ids': [(4, self.id)],
            }