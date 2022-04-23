import uuid
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.fields import Date
import datetime 
from odoo.exceptions import ValidationError

from werkzeug.urls import url_encode


class RaiseAppraisal(models.TransientModel):
    _name = 'raise.appraisal.wizz'
    _description = 'To Raise Appraisal for Eligible employees'


    @api.onchange('appraisal_period','appraisal_deadline')
    def _get_elligible_employees(self):
        for rec in self:
            if self.env.company.id == 1:
                if rec.appraisal_period:
                    prev_year = rec.appraisal_period.date_from.year - 1
                    rec.appraisal_deadline = datetime.datetime.strptime('30-09-'+str(prev_year),  '%d-%m-%Y')

                    if rec.appraisal_deadline:
                        s_lines = [(5,0,0)]
                        lines = self.env['hr.employee'].search([('date_of_joining','<=',rec.appraisal_deadline),('company_id','=',self.env.company.id)])
                        for l in lines:
                            res = {
                             'employee_id': l.id,
                             'current_designation':l.job_id.id,
                             'appraisal_wiz_id': rec.id,
                             'is_designation_changed': None,
                             'new_designation': None,
                            }
                            s_lines.append((0,0,res))

                        rec.elligible_employee_ids = s_lines
            else:
                if rec.appraisal_period:
                    # prev_year = rec.appraisal_period.date_from.year - 1
                    rec.appraisal_deadline = datetime.date.today()

                    if rec.appraisal_deadline:
                        s_lines = [(5,0,0)]
                        lines = self.env['hr.employee'].search([('date_of_joining','<=',rec.appraisal_deadline),('company_id','=',self.env.company.id)])
                        for l in lines:
                            no_days = datetime.date.today() - l.date_of_joining

                            if no_days.days >= 365:
                                res = {
                                 'employee_id': l.id,
                                 'current_designation':l.job_id.id,
                                 'appraisal_wiz_id': rec.id,
                                 'is_designation_changed': None,
                                 'new_designation': None,
                                }
                                s_lines.append((0,0,res))

                        rec.elligible_employee_ids = s_lines

    appraisal_period = fields.Many2one('account.fiscal.year',domain=lambda self: [('company_id', '=', self.env.company.id)])
    appraisal_deadline = fields.Date()
    # appraisal_start_date = fields.Date()
    # company_id = fields.Many2one('res.company', default=lamba self: self.env.company.id)
    appraisal_end_date = fields.Date(default=lambda self: datetime.date.today().replace(day=1)+relativedelta(months=+1, days=-1))
    elligible_employee_ids = fields.One2many('appraisal.elligible.employees','appraisal_wiz_id')



    def raise_appraisal(self):
        if self.elligible_employee_ids:
            for line in self.elligible_employee_ids:
                self.env['hr.appraisal'].create({
                    'employee_id':line.employee_id.id,
                    'is_designation_changed':line.is_designation_changed,
                    'new_designation':line.new_designation.id,
                    'state':'pending',
                    'appraisal_period':self.appraisal_period.id,
                    })

            return   {
                'type': 'ir.actions.client',
                'tag': 'reload',
                }



class ElligibleEmployees(models.TransientModel):

    _name = 'appraisal.elligible.employees'
    _description = "line ids for elligible candidates"

    employee_id = fields.Many2one('hr.employee',string='Employee')
    current_designation = fields.Many2one('hr.job', compute="get_position")
    appraisal_wiz_id = fields.Many2one('raise.appraisal.wizz')
    is_designation_changed = fields.Boolean()
    new_designation = fields.Many2one('hr.job')


    @api.depends('employee_id')
    def get_position(self):
        for rec in self:
            if rec.employee_id.job_id:
                rec.current_designation = rec.employee_id.job_id.id
            else:
                rec.current_designation = None 




    