from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    demands_id = fields.Many2one(
        'demands', string='Demands', check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")