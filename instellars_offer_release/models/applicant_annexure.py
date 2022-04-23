# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _,SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class Annexures(models.Model):
    _name = 'hr.applicant.annexure'
    _description = 'Annexures For Offer Letter'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def _default_stage_id(self):
        state = self.env.ref('instellars_offer_release.hr_annexure_inactive', raise_if_not_found=False)
        return state if state and state.id else False

    def _get_default_note(self):
        result = """
        ** Net Take home is further subject to reduce by an amount equivalent to Professional Tax and TDS(Income Tax on salary)
        ** As per the Statutory requirement, equal amount will be contributed to the employee’s Provident Fund and same will be deducted from Monthly gross salary of the employee
        """
        return result

    ref_no = fields.Char("Ref",required=True, readonly=True, copy=False, default='New')

    name = fields.Char('Annexures Reference', required=True)
    active = fields.Boolean(default=True)
    applicant_id = fields.Many2one('hr.applicant', string='Applicant', tracking=True)
    applicant_name = fields.Char(related='applicant_id.partner_name')
    job_id = fields.Many2one('hr.job', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", string='Job Position')
    wage = fields.Monetary('Wage', required=True, tracking=True, help="Employee's CTC per Year.")
    medical_allowance = fields.Monetary('Medical Allowance(MA)', tracking=True,default="15000")
    conveyance = fields.Monetary('Conveyance(SA)',tracking=True,default="19200")
    advantages = fields.Text('Advantages')
    notes = fields.Text('Notes', default=_get_default_note)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    preferred_country = fields.Many2one('res.country')
    # state = fields.Selection([
    #     ('draft', 'New'),
    #     ('open', 'Running'),
    #     ('close', 'Expired'),
    #     ('cancel', 'Cancelled')
    # ], string='Status', group_expand='_expand_states', copy=False,
    #    tracking=True, help='Status of the annexure', default='draft')
    state = fields.Many2one('hr.annexure.state', string='Status', group_expand='_read_group_stage_ids', copy=False,
       tracking=True, help='Status of the annexure', default=_default_stage_id)

    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')
    ], string='Kanban State', default='normal', tracking=True, copy=False)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    hr_responsible_id = fields.Many2one('res.users', 'HR Responsible', tracking=True,
        help='Person responsible for validating the applicants\'s annexures.')

    struct_id = fields.Many2one('hr.payroll.structure', string="Structure")
    employement_loc_ind = fields.Many2one('hr.location')
    employement_loc_others = fields.Many2one('hr.location')

    line_ids = fields.One2many('hr.annexure.line', 'annexure_id', string='Payslip Lines')


    @api.model
    def create(self, vals):
        if vals.get('ref_no', 'New') == 'New':
            vals['ref_no'] = self.env['ir.sequence'].next_by_code('hr.applicant.annexure') or 'New'       

        result = super(Annexures, self).create(vals)     

        return result


    def _read_group_stage_ids(self, stages, domain, order):
        # return [key for key, val in type(self).state.many2one]
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    def compute_sheet(self):
        for rec in self:
            rec.line_ids.unlink()
            lines = [(0, 0, line) for line in rec._get_annexures_lines()]
            rec.write({'line_ids': lines})
        return True


    def _get_annexures_lines(self):
        self.ensure_one()
        result = {}
        rules_dict = {}


        applicant = self.applicant_id
        annexure = self.id

        basic = 0.0
        hra = 0.0
        lta = 0.0
        pf =0.0
        ctc = 0.0
        cca = 0.0
        boa = 0.0
        ma = 0.0
        sa = 0.0
        net = 0.0
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            monthly_tot = 0.0
            yearly_tot = 0.0
            if rule.code == 'BASIC':
                yearly_tot = self.wage *(40/100)
                basic = yearly_tot

            if rule.code == 'HRA':
                yearly_tot = basic*(40/100)
                hra = yearly_tot

            if rule.code == 'LTA':
                yearly_tot = basic*(10/100)
                lta = yearly_tot

            if rule.code == 'CTC':
                yearly_tot = self.wage
                ctc = yearly_tot

            if rule.code == 'MA':
                yearly_tot = self.medical_allowance
                ma = yearly_tot

            if rule.code == 'SA':
                yearly_tot = self.conveyance
                sa = yearly_tot

            if rule.code == 'NET':
                yearly_tot = basic + hra + lta + ma + sa + cca + pf
                net = yearly_tot



            if rule.code == 'CCA':
                yearly_tot = ((ctc*(60/100))-pf)-(hra + lta + ma + sa)
                cca = yearly_tot

            if rule.code == 'BOA':
                yearly_tot = hra + lta + sa + ma + cca
                boa = yearly_tot

            if rule.code =='PF':
                if basic <= 180000:
                    yearly_tot = basic*(12/100)
                    pf = yearly_tot
                else:
                    yearly_tot = 180000*(12/100)
                    pf = yearly_tot


            result[rule.code] = {
                'sequence': rule.sequence,
                'code': rule.code,
                'name': rule.name,
                'note': rule.note,
                'salary_rule_id': rule.id,
                'annexure_id': annexure,
                'applicant_id': applicant.id,
                'monthly_total': yearly_tot/12,
                'yearly_total': yearly_tot,
                # 'rate': rate,
                # 'slip_id': self.id,
            }
        return result.values()


    #offer Details india
    offer_type_ind = fields.Selection([('regular','Regular'), ('regular_jb','Regular+JB'),('onditional','Conditional'), ('conditional_jb','Conditional+JB')])
    offer_type_others = fields.Selection([('regular','Regular')])
    # offered_salary_ind = fields.Float()

    # #regular+jb
    # is_jb_conditional = fields.Selection([('yes','Yes'),('no','No')])
    # jb_date = fields.Date()
    # jb_amount = fields.Float()
    # jb_amount_deposited_on = fields.Selection([((str(r)+'_months'), (str(r)+' Months')) for r in range(1, 13)])

    # #offer condition
    # offer_condition = fields.Selection([('clear_client_interview','To clear the Client Interview')])

    # #jb_condition is YES
    # jb_condition = fields.Selection([('join_before','Join Before')])


    # #offer details other country
    offered_salary_other =fields.Float()



    @api.onchange('state')
    def check_for_duplicate_in_active_state(self):
        for rec in self:
            if rec.state.id == 2:
                same_records = self.env['hr.applicant.annexure'].search([('applicant_id','=',rec.applicant_id.id),('state','=',2),('preferred_country','=',rec.preferred_country.id)])
                if same_records:
                    raise ValidationError(_('There is already one active Annexure For this Applicant. Refresh the Page and change state to inactive to continue this process'))




    @api.onchange('applicant_id')
    def _onchange_applicant_id(self):
        if self.applicant_id:
            self.job_id = self.applicant_id.job_id
            self.company_id = self.applicant_id.company_id
            self.wage = self.applicant_id.offered_salary_ind
            self.offer_type_ind = self.applicant_id.offer_type_ind
            # self.offered_salary_ind = self.applicant_id.offered_salary_ind
            # self.is_jb_conditional = self.applicant_id.is_jb_conditional
            # self.jb_date = self.applicant_id.jb_date
            # self.jb_amount = self.applicant_id.jb_amount
            # self.jb_amount_deposited_on = self.applicant_id.jb_amount_deposited_on
            # self.offer_condition = self.applicant_id.offer_condition
            # self.jb_condition = self.applicant_id.jb_condition
            # self.offer_type_others = self.applicant_id.offer_type_others
            # self.offered_salary_other = self.applicant_id.offered_salary_other


class HrPayslipLine(models.Model):
    _name = 'hr.annexure.line'
    _description = 'Annexures Line'
    _order = 'annexure_id, sequence, code'

    name = fields.Char(required=True, translate=True)
    note = fields.Text(string='Description')
    sequence = fields.Integer(required=True, index=True, default=5,
                              help='Use to arrange calculation sequence')
    code = fields.Char(required=True,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                       "In that case, it is case sensitive.")
    # slip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=True)
    annexure_id = fields.Many2one('hr.applicant.annexure', string='Annexure', required=True, index=True)
    applicant_id = fields.Many2one('hr.applicant', string='applicant', required=True)
    yearly_total =fields.Float(digits='Payroll',string="Yearly")
    monthly_total =fields.Float(digits='Payroll',string="Monthly")
   
    category_id = fields.Many2one(related='salary_rule_id.category_id', readonly=True, store=True)


    # @api.depends('quantity', 'amount', 'rate')
    # def _compute_total(self):
    #     for line in self:
    #         line.total = float(line.quantity) * line.amount * line.rate / 100



class HrAnnexureStage(models.Model):
    _name = "hr.annexure.state"
    _description = "annexure state"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the annexure state must be unique!')
    ]

    name = fields.Char("State Name", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order when displaying a states.")
    appilcant_id=fields.Many2one("hr.applicant")

