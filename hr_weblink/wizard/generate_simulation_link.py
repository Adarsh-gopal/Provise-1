import uuid

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.exceptions import ValidationError

from werkzeug.urls import url_encode


class GenerateWebLink(models.TransientModel):
    _name = 'generate.weblink.link'
    _description = 'Generate link to get details from user'

    @api.model
    def default_get(self, fields):
        result = super(GenerateWebLink, self).default_get(fields)
        model = self.env.context.get('active_model')
        if model == 'hr.applicant':
            applicant_id = self.env.context.get('active_id')
            applicant = self.env['hr.applicant'].sudo().browse(applicant_id)
            if not applicant.access_token or applicant.access_token_end_date < Date.today():
                applicant.access_token = uuid.uuid4().hex
                applicant.access_token_end_date = Date.today()
            result['applicant_id'] = applicant_id
            
        return result


    applicant_id = fields.Many2one('hr.applicant')
    name = fields.Char(related="applicant_id.partner_name", string="Name")
    
    job_title = fields.Char("Job Title")
    employee_id = fields.Many2one('hr.employee')

    email_to = fields.Char('Email To', compute='_compute_email_to', store=True, readonly=False)
    url = fields.Char('Simulation link', compute='_compute_url')

    @api.depends('employee_id.address_home_id.email', 'applicant_id.email_from')
    def _compute_email_to(self):
        for wizard in self:
            if wizard.employee_id:
                wizard.email_to = wizard.employee_id.address_home_id.email
            elif wizard.applicant_id:
                wizard.email_to = wizard.applicant_id.email_from

    @api.depends( 'applicant_id','job_title')
    def _compute_url(self):
        for wizard in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/onboarding/form/?'
            params = {}
            
            if wizard.applicant_id:
                params['applicant_id'] = wizard.applicant_id.id
                params['token'] = wizard.applicant_id.access_token
            if wizard.job_title:
                params['job_title'] = wizard.job_title
            if params:
                url = url + url_encode(params)
            wizard.url = url

    

    def send_onboarding_link(self):
        try:
            template_id = self.env.ref('hr_weblink.mail_template_send_offer').id
        except ValueError:
            template_id = False
        try:
            template_applicant_id = self.env.ref('hr_weblink.mail_template_send_weblink_applicant').id
        except ValueError:
            template_applicant_id = False
        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        partner_to = False
        if self.employee_id:
            partner_to = self.employee_id.address_home_id
            if not partner_to:
                raise ValidationError(_("No private address defined on the employee!"))
        elif self.applicant_id:
            partner_to = self.applicant_id.partner_id
            if not partner_to:
                partner_to = self.env['res.partner'].create({
                    'is_company': False,
                    'name': self.applicant_id.partner_name,
                    'email': self.applicant_id.email_from,
                    'phone': self.applicant_id.partner_phone,
                    'mobile': self.applicant_id.partner_mobile
                })
                self.applicant_id.partner_id = partner_to

        if self.applicant_id:
            default_model = 'hr.applicant'
            default_res_id = self.applicant_id.id
            default_use_template = bool(template_applicant_id)
            default_template_id = template_applicant_id
        elif self.employee_contract_id:
            default_model = 'hr.contract'
            default_res_id = self.employee_contract_id.id
            default_use_template = bool(template_id)
            default_template_id = template_id
        else:
            default_model = 'hr.contract'
            default_res_id = self.contract_id.id
            default_use_template = bool(template_id)
            default_template_id = template_id

        ctx = {
            'default_model': default_model,
            'default_res_id': default_res_id,
            'default_use_template': default_use_template,
            'default_template_id': default_template_id,
            'default_composition_mode': 'comment',
            'salary_package_url': self.url,
            'custom_layout': "mail.mail_notification_light",
            'partner_to': partner_to and partner_to.id or False,
            'mail_post_autofollow': False,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
