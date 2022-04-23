# -*- coding: utf-8 -*-
from datetime import date
import calendar
import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import models, fields, api, _
from odoo.addons.web_grid.models.models import END_OF, STEP_BY, START_OF
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression


class Timesheet(models.Model):

    _inherit = 'account.analytic.line'

    manager_approval_state = fields.Selection([('pending_submission','Pending Submission'),('pending_approval','Pending Approval'),('approved','Approved'),('resubmit','Resubmit')], default='pending_approval')
    resubmit_reason = fields.Text()


    @api.depends('date', 'employee_id.timesheet_validated','manager_approval_state')
    def _compute_timesheet_validated(self):
        for line in self:
            if line.is_timesheet:
                # get most recent validation date on any of the line user's employees
                validated_to = line.sudo().employee_id.timesheet_validated
                if validated_to:
                    if line.date <= validated_to and line.manager_approval_state == 'approved':
                        line.validated = True
                    else:
                        line.validated = False
                else:
                        line.validated = False

            else:
                line.validated = True


    def action_validate_timesheet(self):
        if self.env.context.get('grid_anchor'):
            anchor = fields.Date.from_string(self.env.context['grid_anchor'])
        else:
            anchor = date.today() + relativedelta(weeks=-1, days=1, weekday=0)
        span = self.env.context.get('grid_range', 'week')
        validate_to = anchor + END_OF[span]

        if not self:
            raise UserError(_("There aren't any timesheet to validate"))

        domain = self.env['ir.rule']._compute_domain(self._name, 'write')  # can write on the timesheet of team employee or all

        employees = self.filtered_domain(domain or []).mapped('employee_id')

        employees = employees.sudo().filtered(lambda e: not e.timesheet_validated or e.timesheet_validated < validate_to)

        if not employees:
            raise UserError(_('All selected timesheets for which you are indicated as responsible are already validated.'))
        validation = self.env['timesheet.validation'].create({
            'validation_date': validate_to,
            'validation_line_ids': [
                (0, 0, {'employee_id': employee.id}) for employee in employees
            ]
        })

        return {
            'name': _('Validate the timesheets'),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_model': 'timesheet.validation',
            'res_id': validation.id,
            'views': [(False, 'form')],
        }




class ProjectProject(models.Model):
    _inherit = 'project.project'


    def send_manager_approve_status(self,emp, mnt, project):

        if emp and mnt and project:
            dt = datetime.datetime.strptime(mnt,'%b %Y')
            month_range = calendar.monthrange(dt.year, dt.month)


            start_date = datetime.date(dt.year, dt.month, 1)
            end_date = datetime.date(dt.year, dt.month, month_range[1])

            tmsheets = self.env['account.analytic.line'].sudo().search([('project_id','=',project.id),('employee_id','=',emp.id),('date','<=',end_date),('date','>=',start_date)])

            not_yt_submitted = tmsheets.filtered(lambda x: x.manager_approval_state in ['pending_submission','resubmit'])
            submitted = tmsheets.filtered(lambda x: x.manager_approval_state == 'pending_approval')
            approved = tmsheets.filtered(lambda x: x.manager_approval_state == 'approved')

            if not_yt_submitted:
                return "pending_submission"
            elif submitted:
                return "pending_approval"
            else:
                return "approved"









    # def _timesheet_get_portal_domain(self):
    #     domain = super(AnalyticLine, self)._timesheet_get_portal_domain()
    #     param_invoiced_timesheet = self.env['ir.config_parameter'].sudo().get_param('sale.invoiced_timesheet', DEFAULT_INVOICED_TIMESHEET)
    #     if param_invoiced_timesheet == 'approved':
    #         domain = expression.OR([domain, [('validated', '=', False)]])
    #     if param_invoiced_timesheet == 'all':
    #         domain = expression.AND([domain, ['|',('validated', '=', False),('validated', '=', True)]])
    #     return domain
