import uuid

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    resource_id  = fields.Many2one('hr.employee', compute="get_resource_id")

    @api.depends('demands_id')
    def get_resource_id(self):
        for rec in self:
            if rec.demands_id != False:
                rec.resource_id = rec.demands_id.employee_assigned