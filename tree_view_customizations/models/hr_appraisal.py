import uuid

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'hr.appraisal'


    emp_id = fields.Char('Employee ID', compute="get_emp_id")

    @api.depends('employee_id')
    def get_emp_id(self):
        for rec in self:
            rec.emp_id = rec.employee_id.registration_number


