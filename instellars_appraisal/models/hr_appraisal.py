from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _,SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval



class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"

    appraisal_reference = fields.Char(copy=False,tracking=True, default=lambda self: _('New'))
    current_designation = fields.Many2one('hr.job', tracking=True, compute="get_employee_defaults")

    is_designation_changed = fields.Boolean('Is Designation Changed?')
    appraisal_period = fields.Many2one('account.fiscal.year',domain=lambda self: [('company_id', '=', self.env.company.id)])

    state = fields.Selection(selection_add=[('done','Appraisal Received'),('pending_app_calc','Appraisal Pending Calculation'),('app_calc','Appraisal Calculation'),('approved','Appraisal Approved'),('cancel','Appraisal Rejected')],string='Status', tracking=True, required=True, copy=False, default='new', index=True)

    #fields inside page
    overall_performance = fields.Selection([
        ('HE', 'HE'),
        ('E+', 'E+'),
        ('E', 'E'),
        ('E-', "E-"),
        ('ME', "ME"),
    ], string='Overall Performance Rating', tracking=True,  copy=False,  index=True)
    current_fy = fields.Char('Current FY')
    net_salary = fields.Float(tracking=True, compute="get_employee_defaults")

    appraisal_percentage = fields.Float()
    new_net_salary = fields.Float(tracking=True,readonly=True)
    new_designation = fields.Many2one('hr.job',tracking=True)
    medical_allowance = fields.Float('Medical Allowance(MA)', tracking=True,default="15000")
    conveyance = fields.Float('Conveyance(SA)',tracking=True,default="19200")
    struct_id = fields.Many2one('hr.payroll.structure', string="structure")
    appraisal_line_ids = fields.One2many('hr.appraisal.annexure', 'appraisal_id', tracking=True, string='Payslip Lines')


    def calcluate_new_net_salary(self):
        for rec in self:
            if rec.appraisal_percentage:
                current_sal = rec.net_salary
                percent_increase = current_sal *(rec.appraisal_percentage/100)
                rec.write({'new_net_salary': current_sal + percent_increase})
        return True



    @api.depends('employee_id')
    def get_employee_defaults(self):
        for rec in self:
            rec.current_designation = rec.employee_id.job_id.id
            rec.net_salary = rec.employee_id.offered_salary


    @api.model
    def create(self, vals):
        if vals.get('appraisal_reference', 'New') == 'New':
            vals['appraisal_reference'] = self.env['ir.sequence'].next_by_code('hr.appraisal.ref.no') or 'New'       

        result = super(HrAppraisal, self).create(vals)     

        return result


    def compute_sheet(self):
        for rec in self:
            rec.appraisal_line_ids.unlink()
            lines = [(0, 0, line) for line in rec._get_annexures_lines()]
            rec.write({'appraisal_line_ids': lines})
        return True


    def _get_annexures_lines(self):
        self.ensure_one()
        result = {}
        rules_dict = {}


        employee = self.employee_id
        appraisal = self.id

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
                yearly_tot = self.new_net_salary *(40/100)
                basic = yearly_tot

            if rule.code == 'HRA':
                yearly_tot = basic*(40/100)
                hra = yearly_tot

            if rule.code == 'LTA':
                yearly_tot = basic*(10/100)
                lta = yearly_tot

            if rule.code == 'CTC':
                yearly_tot = self.new_net_salary
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
                'appraisal_id': appraisal,
                'employee_id': employee.id,
                'monthly_total': yearly_tot/12,
                'yearly_total': yearly_tot,
                # 'rate': rate,
                # 'slip_id': self.id,
            }
        return result.values()

    sign_request_count = fields.Integer(compute='_compute_sign_request_count')

    def _compute_sign_request_count(self):
        for rec in self:
            sign_from_role = self.env['sign.request.item'].search([
                ('partner_id', '=', rec.employee_id.user_id.partner_id.id),
                ('sign_request_id.reference', 'ilike', 'PMDB'),
                ('role_id', '=', self.env.ref('sign.sign_item_role_employee').id)]).mapped('sign_request_id')

            rec.sign_request_count = len(sign_from_role)

    def open_employee_sign_requests(self):
        self.ensure_one()
        
        sign_from_role = self.env['sign.request.item'].search([
            ('partner_id', '=', self.employee_id.user_id.partner_id.id),
            ('sign_request_id.reference', 'ilike', 'PMDB'),
            ('role_id', '=', self.env.ref('sign.sign_item_role_employee').id)]).mapped('sign_request_id')
        sign_request_ids = sign_from_role
        if len(sign_request_ids.ids) == 1:
            return sign_request_ids.go_to_document()

        if self.env.user.has_group('sign.group_sign_user'):
            view_id = self.env.ref("sign.sign_request_view_kanban").id
        else:
            view_id = self.env.ref("hr_contract_sign.sign_request_employee_view_kanban").id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Signature Requests',
            'view_mode': 'kanban',
            'res_model': 'sign.request',
            'view_id': view_id,
            'domain': [('id', 'in', sign_request_ids.ids)]
        }


    def send_appraisal(self):
        template = self.env.ref('instellars_appraisal.appraisal_letter_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model="hr.appraisal",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            mail_post_autofollow = False,
            custom_layout='mail.mail_notification_light',
        )
        return {
            
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('state')
    def check_aprover_access(self):
        for rec in self:
            if rec.state == 'approved':
                if self.env.user.has_group('instellars_appraisal.allow_change_appraisal_state'):
                    continue
                else:
                    raise UserError(_('You are not supposed to move to this state!. Please Refresh the page for changes!'))



    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override read_group to always display all states and order them appropriatly. """
        if groupby and groupby[0] == "state":
            states = [('new', _('To Start')),('pending', _('Appraisal Sent')),('done', _('Appraisal Received')),('pending_app_calc', _('Appraisal Pending Calculation')),('app_calc', _('Appraisal Calculation')),('approved', _('Appraisal Approved')),('cancel', _('Appraisal Rejected'))]
            read_group_all_states = [{
                '__context': {'group_by': groupby[1:]},
                '__domain': domain + [('state', '=', state_value)],
                'state': state_value,
                'state_count': 0,
            } for state_value, state_name in states]
            # Get standard results
            read_group_res = super(HrAppraisal, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby)
            # Update standard results with default results
            result = []
            for state_value, state_name in states:
                res = [x for x in read_group_res if x['state'] == state_value]
                if not res:
                    res = [x for x in read_group_all_states if x['state'] == state_value]
                res[0]['state'] = state_value
                if res[0]['state'][0] == 'done' or res[0]['state'][0] == 'cancel':
                    res[0]['__fold'] = True
                result.append(res[0])
            print(result,'*****************************************')
            return result
        else:
            return super(HrAppraisal, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby)



class HrAppraisalAnnexure(models.Model):
    _name = 'hr.appraisal.annexure'
    _description = 'Appraisal Annexures Line'
    _order = 'appraisal_id, sequence, code'

    name = fields.Char(required=True, translate=True)
    note = fields.Text(string='Description')
    sequence = fields.Integer(required=True, index=True, default=5,
                              help='Use to arrange calculation sequence')
    code = fields.Char(required=True,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                       "In that case, it is case sensitive.")
    # slip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=True)
    appraisal_id = fields.Many2one('hr.appraisal', string='Appraisal', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='employee', required=True)
    yearly_total =fields.Float(digits='Payroll',string="Yearly")
    monthly_total =fields.Float(digits='Payroll',string="Monthly")
   
    category_id = fields.Many2one(related='salary_rule_id.category_id', readonly=True, store=True)