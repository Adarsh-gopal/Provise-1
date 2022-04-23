from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class HrApplicant(models.Model):
    _inherit = 'hr.applicant' 
    access_token = fields.Char('Security Token', copy=False)
    access_token_end_date = fields.Date('Access Token Validity Date', copy=False)

    enable_on_board = fields.Boolean(compute='get_stage_onboard_value')

    @api.depends('stage_id')
    def get_stage_onboard_value(self):
        for rec in self:
            rec.enable_on_board = rec.stage_id.enable_on_board

    # def action_show_proposed_contracts(self):
    #     return {
    #         "type": "ir.actions.act_window",
    #         "res_model": "hr.contract",
    #         "views": [[False, "tree"], [False, "form"]],
    #         "domain": [["applicant_id", "=", self.id], '|', ["active", "=", False], ["active", "=", True]],
    #         "name": "Proposed Contracts",
    #         "context": {'default_employee_id': self.emp_id.id},
    #     }

    # def _compute_proposed_contracts_count(self):
    #     Contracts = self.env['hr.contract'].sudo()
    #     for applicant in self:
    #         applicant.proposed_contracts_count = Contracts.with_context(active_test=False).search_count([
    #             ('applicant_id', '=', applicant.id)])

class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    #need aproval checkbox at stages to check weather that stage needs aproval
    enable_on_board = fields.Boolean()

