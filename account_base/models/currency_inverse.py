# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    inverse_rate = fields.Float(digits=(12, 3))

    @api.onchange('inverse_rate')
    def onchange_inverse(self):
        if self.inverse_rate:
            self.rate = 1/self.inverse_rate
        else:
            self.rate = 0