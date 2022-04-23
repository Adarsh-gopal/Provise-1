from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _,SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class Annexures(models.Model):
    _inherit = 'hr.applicant.annexure'


    appraisal_count = fields.Integer(compute='_compute_appraisals', string="Appraisal Count")


    def _compute_appraisals(self):
        for rec in self:
            if rec.applicant_id:
                if rec.applicant_id.emp_id:
                    appraisal = self.env['hr.appraisal'].search([('employee_id', '=', rec.applicant_id.emp_id.id)])
                    rec.appraisal_count = len(appraisal)
                else:
                    rec.appraisal_count = 0


    def filter_appraisal(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appraisals',
            'view_mode': 'tree',
            'res_model': 'hr.appraisal',
            'domain': [('employee_id', 'in', self.applicant_id.emp_id.ids)],
            'context': "{'create': False}"
        }




