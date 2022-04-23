from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    due_date = fields.Date()
    purchase_order_number = fields.Char()
    purchase_order_date = fields.Date()
    vendor_code = fields.Char(compute="get_vendor_code", store=True)

    @api.depends('partner_id')
    def get_vendor_code(self):
        for rec in self:
            rec.vendor_code = rec.partner_id.vendor_code


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	resource_name = fields.Many2one('hr.employee')
	service_period_from = fields.Date()
	service_period_to = fields.Date()




