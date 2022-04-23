from odoo import api, fields, models


# class MailActivityType(models.Model):
#     _inherit = 'mail.activity.type'

#     template_id = fields.Many2one('mail.template')


class CalendarEvent(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'


    interviewer = fields.Many2many('res.users')
    interviewee = fields.Many2one('res.partner', compute="get_employee_user")
    interview_location = fields.Many2one('res.company' )
    note = fields.Text()

    #zoom interview
    meeting_id = fields.Char('meeting id')
    password = fields.Char()
    zoom_link = fields.Char()

    #skype call
    skype_link = fields.Char()

    activity_type=fields.Many2one('mail.activity.type')
    category_name = fields.Char(compute="get_category_name")
    activity_type_name = fields.Char(compute="get_category_name")

    # igc_resume = fields.Binary()

    @api.onchange('interviewer')
    def add_interviwer_email(self):
        if self.interviewer:
            partner_ids = [user.partner_id.id for user in self.interviewer]
            self.partner_ids = [(6, 0, partner_ids)]
            # self.partner_ids = [(4, user.partner_id.id) for user in self.interviewer]
        

    @api.onchange('interviewee')
    def add_interviewee(self):
        if self.interviewee:
            self.partner_ids = [(4, self.interviewee.id)]

    @api.depends('res_model','applicant_id')
    def get_employee_user(self):
        for rec in self:
            if rec.applicant_id:
                if rec.applicant_id.partner_id:
                    rec.interviewee = rec.applicant_id.partner_id.id
                    rec.partner_ids = [(4, rec.applicant_id.partner_id.id)]
                else:
                    rec.interviewee = False
            elif rec.res_id and rec.res_model == 'hr.applicant':
                applicant = self.env[rec.res_model].browse(rec.res_id)
                rec.applicant_id = applicant.id
                if applicant.partner_id:
                    rec.interviewee = applicant.partner_id.id
                    rec.partner_ids = [(4, applicant.partner_id.id)]
                else:
                    rec.interviewee = False
            else:
                rec.interviewee = False


    @api.depends('activity_type')
    def get_category_name(self):
        for rec in self:
            if rec.activity_type:
                rec.category_name=rec.activity_type.category
                rec.activity_type_name=rec.activity_type.name
            else:
                rec.category_name = False
                rec.activity_type_name = False


    def create_attendees(self):
        current_user = self.env.user
        result = {}
        for meeting in self:
            alreay_meeting_partners = meeting.attendee_ids.mapped('partner_id')
            meeting_attendees = self.env['calendar.attendee']
            meeting_partners = self.env['res.partner']
            for partner in meeting.partner_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'event_id': meeting.id,
                }

                if self._context.get('google_internal_event_id', False):
                    values['google_internal_event_id'] = self._context.get('google_internal_event_id')

                # current user don't have to accept his own meeting
                if partner == self.env.user.partner_id:
                    values['state'] = 'accepted'

                attendee = self.env['calendar.attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= partner

            if meeting_attendees and not self._context.get('detaching'):
                # print(self._context.get('detaching'),meeting_attendees,'*************************')
                to_notify = meeting_attendees.filtered(lambda a: a.email != current_user.email)
                if self.res_model == 'hr.applicant':
                    print('hr applicant model')
                    if self.activity_type_name == 'F2F Interview':
                        to_notify._send_mail_to_attendees('instellars_interview_schedule.calendar_template_meeting_invitation_f2f')
                    elif self.activity_type_name == 'Zoom Interview':
                        to_notify._send_mail_to_attendees('instellars_interview_schedule.calendar_template_meeting_invitation_zoom_interview')
                    elif self.activity_type_name == 'Skype Interview':
                        to_notify._send_mail_to_attendees('instellars_interview_schedule.calendar_template_meeting_invitation_skype_interview')
                    elif self.activity_type_name == 'Telephonic Interview':
                        to_notify._send_mail_to_attendees('instellars_interview_schedule.calendar_template_meeting_invitation_telephonic_interview')
                    else:
                        to_notify._send_mail_to_attendees('calendar.calendar_template_meeting_invitation')
                else:
                    to_notify._send_mail_to_attendees('calendar.calendar_template_meeting_invitation')

            if meeting_attendees:
                meeting.write({'attendee_ids': [(4, meeting_attendee.id) for meeting_attendee in meeting_attendees]})

            if meeting_partners:
                meeting.message_subscribe(partner_ids=meeting_partners.ids)

            # We remove old attendees who are not in partner_ids now.
            all_partners = meeting.partner_ids
            all_partner_attendees = meeting.attendee_ids.mapped('partner_id')
            old_attendees = meeting.attendee_ids
            partners_to_remove = all_partner_attendees + meeting_partners - all_partners

            attendees_to_remove = self.env["calendar.attendee"]
            if partners_to_remove:
                attendees_to_remove = self.env["calendar.attendee"].search([('partner_id', 'in', partners_to_remove.ids), ('event_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_attendees,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': partners_to_remove
            }
        return result


