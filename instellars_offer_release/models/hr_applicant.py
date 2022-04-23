from odoo import fields, models, api,_
from datetime import datetime, timedelta, date


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'


    status= fields.Selection([('cleared','Cleared'),('rejected','Rejected'),('re_scheduled','Re-Scheduled'),('reject_by_candidate','Rejected By Candidate')])
    scheduled_with = fields.Many2one('res.users')
    scheduled_on = fields.Datetime()
    preferred_country = fields.Many2one('res.country')
    offer_date_of_join = fields.Date()
    candidate_pedology = fields.Selection([('lead_architect','Lead Architect'),('individual_contributor','Individual Contributor'),('senior','Senior'),('mid_level','Mid Level'),('juinor','Juinor')])
    visa_deposit = fields.Selection([('yes','Yes'),('no','No')])
    visa_deposit_amount = fields.Float()
    visa_deposit_refundable = fields.Selection([('yes','Yes'),('no','No')])
    visa_deposit_refundable_month = fields.Selection([('after_3_months','After 3 Months'),('after_6_months','After 6 Months'),('after_8_months','After 8 Months'),('after_12_months','After 12 Months')])

    #offer Details india
    offer_type_ind = fields.Selection([('regular','Regular'), ('regular_jb','Regular+JB'),('onditional','Conditional'), ('conditional_jb','Conditional+JB')])
    offered_salary_ind = fields.Float()

    #regular+jb
    is_jb_conditional = fields.Selection([('yes','Yes'),('no','No')])
    jb_date = fields.Date()
    jb_amount = fields.Float()
    jb_amount_deposited_on = fields.Selection([((str(r)+'_months'), (str(r)+' Months')) for r in range(1, 13)])

    #offer condition
    offer_condition = fields.Selection([('clear_client_interview','To clear the Client Interview')])

    #jb_condition is YES
    jb_condition = fields.Selection([('join_before','Join Before')])


    #offer details other country
    offer_type_others = fields.Selection([('regular','Regular')])
    offered_salary_other =fields.Float()

    #reject reason &rescheduling reason
    rejected_reason = fields.Many2one('hr.reject.reason')
    re_scheduled_reason = fields.Many2one('reschedule.reason')
    employement_loc_ind = fields.Many2one('hr.location')
    employement_loc_others = fields.Many2one('hr.location')

    #feedback
    feedback = fields.Text()

    #sceenshots and skypecall list
    skype_records = fields.Binary("Attachment Screenshot or Skype Record")
    attach_audio = fields.Binary()


    #annexures count for smart buttons
    annexure_count = fields.Integer(compute='_compute_annexures_count', string="Annexures Count")
    annexure_id =fields.Many2one('hr.applicant.annexure')

    # evaluation_form = fields.Html('evaluation form',track_visibility="", tracking=True)

    def _compute_annexures_count(self):
        annxures_data = self.env['hr.applicant.annexure'].read_group([('applicant_id', 'in', self.ids)], ['applicant_id'], ['applicant_id'])
        result = dict((data['applicant_id'][0], data['applicant_id_count']) for data in annxures_data)
        # print(annxures_data,'*************************')
        annexure = self.env['hr.applicant.annexure'].search([('applicant_id', '=', self.id),('state','=',2)])
        # print(annexure,"******************************************")
        for rec in self:
            rec.annexure_count = result.get(rec.id, 0)
            rec.annexure_id = annexure.id

    def filter_annexure(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Annexure-I',
            'view_mode': 'kanban,tree,form',
            'res_model': 'hr.applicant.annexure',
            'domain': [('applicant_id', 'in', self.ids)],
            'context': "{'create': False}"
        }


    def send_offer(self):
        try:
            template_applicant_id = self.env.ref('instellars_offer_release.offer_letter_template').id
        except ValueError:
            template_applicant_id = False
        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        partner_to = False
        if self.env.context.get('active_id'):
            applicant_id = self.env['hr.applicant'].sudo().browse(self.env.context.get('active_id'))
            partner_to = self.partner_id
            if not partner_to:
                partner_to = self.env['res.partner'].create({
                    'is_company': False,
                    'name': self.partner_name,
                    'email': self.email_from,
                    'phone': self.partner_phone,
                    'mobile': self.partner_mobile
                })
                self.partner_id = partner_to

        if self.id:
            default_model = 'hr.applicant'
            default_res_id = self.id
            default_use_template = bool(template_applicant_id)
            default_template_id = template_applicant_id

        ctx = {
            'default_model': default_model,
            'default_res_id': default_res_id,
            'default_use_template': default_use_template,
            'default_template_id': default_template_id,
            'default_composition_mode': 'comment',
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


    enable_offer_letter_button = fields.Boolean(compute='enable_buttons')
    enable_update_result_button = fields.Boolean(compute='enable_buttons')

    enable_appointment_letter = fields.Boolean(compute='enable_buttons')


    @api.depends('stage_id')
    def enable_buttons(self):
        for rec in self:
            rec.enable_offer_letter_button = rec.stage_id.enable_offer_letter_button
            rec.enable_update_result_button = rec.stage_id.enable_update_result_button
            rec.enable_appointment_letter = rec.stage_id.enable_appointment_letter

    def send_appointment_letter(self):
        template = self.env.ref('instellars_offer_release.appointment_letter_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model="hr.applicant",
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


class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    #need aproval checkbox at stages to check weather that stage needs aproval
    enable_offer_letter_button = fields.Boolean()
    enable_update_result_button = fields.Boolean()
    enable_appointment_letter = fields.Boolean()









