# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import AccessError, UserError, ValidationError, Warning


class ValidationWizard(models.TransientModel):
    _inherit = 'timesheet.validation'

    timesheet_line_ids = fields.One2many('unapproved.timesheets.lines', 'validation_id', compute="action_check_approval", store=True)
    deselect_all = fields.Boolean()

    @api.onchange('deselect_all')
    def check_n_uncheck(self):
        if self.deselect_all:
            for each in self.validation_line_ids:
                each.validate=False
        else:
            for each in self.validation_line_ids:
                each.validate=True




    @api.depends('validation_line_ids')
    def action_check_approval(self):
        for rec in self:
            if rec.validation_line_ids:
                employees = rec.validation_line_ids.filtered('validate').mapped('employee_id')
                timesheets = self.env['account.analytic.line'].search([('employee_id','in', employees.ids)]).filtered(lambda l: l.manager_approval_state != 'approved' and l.validated == False and l.date <= rec.validation_date)
                if timesheets:

                    timesheet_lines = [(5,0,0)]
                    for l in timesheets:
                        res = {
                        'timesheet_id':l.id,
                        'validation_id': rec.id,
                        }
                        timesheet_lines.append((0,0,res))

                    rec.timesheet_line_ids = timesheet_lines
                else:
                    rec.timesheet_line_ids = None
            else:
                    rec.timesheet_line_ids = None



            # return True


    def action_validate(self):
        employees = self.validation_line_ids.filtered('validate').mapped('employee_id')
        timesheets = self.env['account.analytic.line'].search([('employee_id','in', employees.ids)]).filtered(lambda l: l.manager_approval_state != 'approved' and l.validated == False and l.date <= self.validation_date)

        if timesheets:
            raise ValidationError(' some timesheets not yet approved by manager')

        return super(ValidationWizard, self).action_validate()



class UnApprovedTmsht(models.TransientModel):
    _name = 'unapproved.timesheets.lines'
    _description = 'un approved timesheet line records'

    timesheet_id = fields.Many2one('account.analytic.line')
    validation_id = fields.Many2one('timesheet.validation')
    employee_id = fields.Many2one(related="timesheet_id.employee_id")
    date = fields.Date(related="timesheet_id.date")
    manager_approval_state = fields.Selection(related="timesheet_id.manager_approval_state")







