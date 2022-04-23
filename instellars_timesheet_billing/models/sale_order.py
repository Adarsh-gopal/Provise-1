from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_task_prepare_values(self, project):
        self.ensure_one()
        planned_hours = self._convert_qty_company_hours(self.company_id)
        sale_line_name_parts = self.name.split('\n')
        title = sale_line_name_parts[0] or self.product_id.name
        description = '<br/>'.join(sale_line_name_parts[1:])
        return {
            'name': title if project.sale_line_id else '%s: %s' % (self.order_id.name or '', title),
            'planned_hours': planned_hours,
            'partner_id': self.order_id.partner_id.id,
            'email_from': self.order_id.partner_id.email,
            'description': description,
            'project_id': project.id,
            'sale_line_id': self.id,
            'company_id': project.company_id.id,
            'user_id': self.resource_name.user_id.id if self.resource_name.user_id else False,  # force non assigned task, as created as sudo()
        }

