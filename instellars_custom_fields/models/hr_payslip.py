from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError


class Hrpayslip(models.Model):
    _inherit = 'hr.payslip'

    final_settlement_information = fields.Boolean(string="F&F Payslip")

    #fields for F&F Settlement
    last_working_day_at_instellars= fields.Date()
    submission_date_of_resignation = fields.Date()
    date_of_relieving= fields.Date()
    last_salary_paid_date =fields.Date()
    notice_period_as_per_application = fields.Char()
    notice_period_adjustable = fields.Char()


    @api.onchange('date_to')
    def update_salarydate_to_employee(self):
        if self.final_settlement_information == False:
            employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
            employee.write({'last_salary_paid_date':self.date_to})


    @api.onchange('final_settlement_information','employee_id')
    def get_fandf_informations(self):
        if self.final_settlement_information and self.employee_id:
            self.last_working_day_at_instellars = self.employee_id.last_working_day_at_instellars
            self.submission_date_of_resignation = self.employee_id.submission_date_of_resignation
            self.date_of_relieving = self.employee_id.date_of_relieving
            self.last_salary_paid_date = self.employee_id.last_salary_paid_date
            self.notice_period_as_per_application = self.employee_id.notice_period_as_per_application
            self.notice_period_adjustable = self.employee_id.notice_period_adjustable
