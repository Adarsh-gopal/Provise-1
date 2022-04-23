import uuid

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.exceptions import ValidationError

from werkzeug.urls import url_encode


class GenerateEvalLink(models.TransientModel):
    _name = 'evaluation.link'
    _description = 'Generate evaluation form link to interviewer'

    @api.model
    def default_get(self, fields):
        result = super(GenerateEvalLink, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        record = self.env['calendar.event'].sudo().browse(active_id)
        if record.res_model == 'hr.applicant':
            applicant_id = record.applicant_id.id
            applicant = self.env['hr.applicant'].sudo().browse(applicant_id)
            # if not applicant.access_token or applicant.access_token_end_date < Date.today():
            #     applicant.access_token = uuid.uuid4().hex
            #     applicant.access_token_end_date = Date.today()
            result['applicant_id'] = applicant_id
            result['stage_id'] = applicant.stage_id.id
            result['event_id'] = record.id

            partner_ids = [user.partner_id.id for user in record.interviewer]
            result['interviewer'] = [(6, 0, partner_ids)]
            result['users'] = [(6, 0, record.interviewer.ids)]

            
        return result

    name = fields.Char('Applicant Name', related='applicant_id.partner_name', readonly=True)
    applicant_id = fields.Many2one('hr.applicant')
    stage_id = fields.Many2one('hr.recruitment.stage')
    
    interviewer = fields.Many2many('res.partner')
    users = fields.Many2many('res.users')
    event_id = fields.Many2one('calendar.event')

    url = fields.Char('Evaluation Web link', compute='_compute_url')

    # @api.depends('employee_id.address_home_id.email', 'applicant_id.email_from')
    # def _compute_email_to(self):
    #     for wizard in self:
    #         if wizard.employee_id:
    #             wizard.email_to = wizard.employee_id.address_home_id.email
    #         elif wizard.applicant_id:
    #             wizard.email_to = wizard.applicant_id.email_from

    @api.depends( 'applicant_id')
    def _compute_url(self):
        for wizard in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/evaluation/form/?'
            params = {}
            
            if wizard.applicant_id:
                params['applicant_id'] = wizard.applicant_id.id
                params['stage_id'] = wizard.applicant_id.stage_id.id
                # user_ids = [str(user.id) for user in wizard.users]
                # print(user_ids,'************************************')
                params['users'] = ','.join([str(cid) for cid in wizard.users.ids])
            if params:
                url = url + url_encode(params)
            wizard.url = url

    

    def send_evaluation_form(self):
        try:
            template_applicant_id = self.env.ref('instellars_interview_schedule.mail_template_interview_evaluation_form').id
        except ValueError:
            template_applicant_id = False
        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        partner_to = False
        if self.interviewer:
            partner_mails = [str(user.id) for user in self.interviewer]
            partner_to = ','.join(partner_mails)
            # partner_to = self.interviewer.ids

        ctx = {
            'default_model': self.event_id.res_model,
            'default_res_id': self.event_id.res_id,
            'default_use_template': bool(template_applicant_id),
            'default_template_id': template_applicant_id,
            'default_composition_mode': 'comment',
            'evaluation_form_url': self.url,
            'custom_layout': "mail.mail_notification_light",
            'partner_to': partner_to  or  False,
            'mail_post_autofollow': False,
            'applicants_name':self.applicant_id.partner_name,
            'position':self.applicant_id.job_id.name,
            'stage_name':self.applicant_id.stage_id.name,
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
