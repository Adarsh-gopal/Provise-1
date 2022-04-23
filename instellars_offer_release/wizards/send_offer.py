import uuid

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.exceptions import ValidationError

from werkzeug.urls import url_encode


class OfferRelease(models.TransientModel):
    _name = 'send.offer.letter'
    _description = 'Send offer letter'


    profile_id =fields.Char('Profile ID')
    applicants_name = fields.Char('Name')
    current_ctc = fields.Float('Current CTC')
    expected_ctc = fields.Float('Expected CTC')
    total_years_of_exp = fields.Float('Experience')
    total_relavant_years_of_exp = fields.Float('Relavant Experience')
    notice_period = fields.Integer('Notice Period(Days)')
    notice_period_type = fields.Selection([('serving_np', 'Serving NP'), ('yet_to_serve_np', 'Yet to Serve NP')], string="Notice Period Type")
    designation = fields.Many2one('hr.job')
    employement_loc_ind = fields.Many2one('hr.location')
    employement_loc_others = fields.Many2one('hr.location')


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
    offer_type_ind = fields.Selection([('regular','Regular'), ('regular_jb','Regular+JB'),('conditional','Conditional'), ('conditional_jb','Conditional+JB')])
    offered_salary_ind = fields.Float()

    #regular+jb
    is_jb_conditional = fields.Selection([('yes','Yes'),('no','No')])
    jb_date = fields.Date()
    jb_amount = fields.Float()
    jb_amount_deposited_on = fields.Selection([((str(r)+'_months'), (str(r)+' Months')) for r in range(1, 13)])

    #jb_condition is YES
    jb_condition = fields.Selection([('join_before','Join Before')])

    #offer condition
    offer_condition = fields.Selection([('clear_client_interview','To clear the Client Interview')])


    #offer details other country
    offer_type_others = fields.Selection([('regular','Regular')])
    offered_salary_other =fields.Float()

    #reject reason &rescheduling reason
    rejected_reason = fields.Many2one('hr.reject.reason')
    re_scheduled_reason = fields.Many2one('reschedule.reason')

    feedback = fields.Text()

    stage_name = fields.Char()

    skype_records = fields.Binary("Attachment Screenshot or Skype Record")
    attach_audio = fields.Binary()

    preferred_country = fields.Many2one('res.country')


    @api.model
    def default_get(self, fields):
        result = super(OfferRelease, self).default_get(fields)
        model = self.env.context.get('active_model')
        if model == 'hr.applicant':
            applicant_id = self.env.context.get('active_id')
            applicant = self.env['hr.applicant'].sudo().browse(applicant_id)
            result['applicant_id'] = applicant_id
            result['profile_id'] = applicant.profile_id
            result['applicants_name'] = applicant.partner_name
            result['current_ctc'] = applicant.current_salary
            result['expected_ctc'] = applicant.salary_expected
            result['total_years_of_exp'] = applicant.total_years_of_experience
            result['total_relavant_years_of_exp'] = applicant.relevant_years_of_experience
            result['notice_period'] = applicant.notice_period
            result['notice_period_type'] = applicant.notice_period_type
            result['designation'] = applicant.job_id.id
            result['skype_records'] = applicant.skype_records
            result['attach_audio'] = applicant.attach_audio
            result['stage_name'] = applicant.stage_id.name
            result['status'] = applicant.status
            result['scheduled_with'] = applicant.scheduled_with.id
            result['scheduled_on'] = applicant.scheduled_on
            result['preferred_country'] = applicant.preferred_country.id
            result['offer_date_of_join'] = applicant.offer_date_of_join
            result['candidate_pedology'] = applicant.candidate_pedology
            result['visa_deposit'] = applicant.visa_deposit
            result['visa_deposit_amount'] = applicant.visa_deposit_amount
            result['visa_deposit_refundable'] = applicant.visa_deposit_refundable
            result['visa_deposit_refundable_month'] = applicant.visa_deposit_refundable_month
            result['offer_type_ind'] = applicant.offer_type_ind
            result['offered_salary_ind'] = applicant.offered_salary_ind
            result['is_jb_conditional'] = applicant.is_jb_conditional
            result['jb_date'] = applicant.jb_date
            result['jb_amount'] = applicant.jb_amount
            result['jb_amount_deposited_on'] = applicant.jb_amount_deposited_on
            result['offer_condition'] = applicant.offer_condition
            result['jb_condition'] = applicant.jb_condition
            result['offer_type_others'] = applicant.offer_type_others
            result['offered_salary_other'] = applicant.offered_salary_other
            result['rejected_reason'] = applicant.rejected_reason.id
            result['re_scheduled_reason'] = applicant.re_scheduled_reason.id
            result['feedback'] = applicant.feedback
            result['skype_records'] = applicant.skype_records
            result['attach_audio'] = applicant.attach_audio
            result['employement_loc_ind'] = applicant.employement_loc_ind.id
            result['employement_loc_others'] = applicant.employement_loc_others.id

            
        return result


    applicant_id = fields.Many2one('hr.applicant')
    
    job_title = fields.Char("Job Title")
    employee_id = fields.Many2one('hr.employee')

    email_to = fields.Char('Email To', compute='_compute_email_to', store=True, readonly=False)
    # url = fields.Char('Simulation link', compute='_compute_url')

    @api.depends('employee_id.address_home_id.email', 'applicant_id.email_from')
    def _compute_email_to(self):
        for wizard in self:
            if wizard.employee_id:
                wizard.email_to = wizard.employee_id.address_home_id.email
            elif wizard.applicant_id:
                wizard.email_to = wizard.applicant_id.email_from


    def update(self):
        # for rec in self:
        applicant = self.env['hr.applicant'].sudo().browse(self.applicant_id.id)
        if applicant:
            applicant.write({
                'status': self.status,
                'scheduled_with': self.scheduled_with,
                'scheduled_on': self.scheduled_on,
                'preferred_country': self.preferred_country.id,
                'offer_date_of_join': self.offer_date_of_join,
                'candidate_pedology': self.candidate_pedology,
                'visa_deposit': self.visa_deposit,
                'visa_deposit_amount': self.visa_deposit_amount,
                'visa_deposit_refundable': self.visa_deposit_refundable,
                'visa_deposit_refundable_month': self.visa_deposit_refundable_month,
                'offer_type_ind': self.offer_type_ind,
                'offered_salary_ind': self.offered_salary_ind,
                'is_jb_conditional': self.is_jb_conditional,
                'jb_date': self.jb_date,
                'jb_amount': self.jb_amount,
                'jb_amount_deposited_on': self.jb_amount_deposited_on,
                'jb_condition': self.jb_condition,
                'offer_condition': self.offer_condition,
                'offer_type_others': self.offer_type_others,
                'offered_salary_other': self.offered_salary_other,
                'rejected_reason': self.rejected_reason.id,
                're_scheduled_reason': self.re_scheduled_reason.id,
                'feedback': self.feedback,
                'skype_records': self.skype_records,
                'attach_audio': self.attach_audio,
                'employement_loc_ind': self.employement_loc_ind,
                'employement_loc_others': self.employement_loc_others,
                })
        annexures = self.env['hr.applicant.annexure'].sudo().search([('applicant_id','=',applicant.id),('state','=',2)])
        if annexures:
            raise ValidationError(
                _('Annexures already in Active State Please make it Inactive to create New Annexure')
            )
        else:
            if self.preferred_country.code == 'IN':
                new_rec_india = self.env['hr.applicant.annexure'].create({
                    'name':applicant.partner_name +'\'s' + ' Offer Annexures I India',
                    'applicant_id':applicant.id,
                    'job_id':applicant.job_id.id,
                    'employement_loc_ind':applicant.employement_loc_ind.id,
                    'preferred_country':104,
                    'wage':applicant.offered_salary_ind,
                    'offer_type_ind':applicant.offer_type_ind,
                    })
            else:
                new_rec_india = self.env['hr.applicant.annexure'].create({
                    'name':applicant.partner_name +'\'s' + ' Offer Annexures I India',
                    'applicant_id':applicant.id,
                    'job_id':applicant.job_id.id,
                    'preferred_country':104,
                    'employement_loc_ind':applicant.employement_loc_ind.id,
                    'wage':applicant.offered_salary_ind,
                    'offer_type_ind':applicant.offer_type_ind,
                    })
                new_rec_others = self.env['hr.applicant.annexure'].create({
                    'name':applicant.partner_name +'\'s' + ' Offer Annexures I others',
                    'applicant_id':applicant.id,
                    'job_id':applicant.job_id.id,
                    'preferred_country':applicant.preferred_country.id,
                    'employement_loc_others':applicant.employement_loc_others.id,
                    'wage':applicant.offered_salary_other,
                    'offer_type_others':applicant.offer_type_others,
                    })






   
