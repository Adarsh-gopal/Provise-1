# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountCashRounding(models.Model):

    _inherit = 'account.cash.rounding'

    activate = fields.Boolean()

    @api.onchange('activate')
    def _onchange_activate(self):
        self.env.cr.execute("""UPDATE account_cash_rounding SET activate = FALSE WHERE activate = TRUE""")


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_cash_rounding_id = fields.Many2one(compute="_calc_rounded_amt",store=True)

    @api.depends('amount_total')
    def _calc_rounded_amt(self):
        for rec in self:
            self.env.cr.execute("""SELECT id FROM account_cash_rounding WHERE activate = TRUE""")
            self.invoice_cash_rounding_id = self.env.cr.fetchone()[0]