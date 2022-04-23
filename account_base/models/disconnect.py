# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        if self.invoice_date:
            if not self.invoice_payment_term_id:
                self.invoice_date_due = self.invoice_date
            self._onchange_currency()