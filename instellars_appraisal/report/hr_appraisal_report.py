from odoo import api, fields, models, tools

from odoo.addons.hr_appraisal.models.hr_appraisal import HrAppraisal

COLORS_BY_STATE = {
    'new': 0,
    'cancel': 1,
    'pending': 2,
    'done': 3,
    'pending_app_calc': 4,
    'app_calc': 5,
    'approved': 6,
}

class HrAppraisalReport(models.Model):
    _inherit = "hr.appraisal.report"

    state = fields.Selection(selection_add=[('done','Appraisal Received'),('pending_app_calc','Appraisal Pending Calculation'),('app_calc','Appraisal Calculation'),('approved','Appraisal Approved'),('cancel','Appraisal Rejected')])


    def _compute_color(self):
        for record in self:
            record.color = COLORS_BY_STATE[record.state]
   