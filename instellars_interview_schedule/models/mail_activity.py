from odoo import api, fields, models, tools,_

class MailActivity(models.Model):
    _inherit = "mail.activity"


    def action_create_calendar_event(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        if self.env.context.get('default_res_model') == 'hr.applicant':
            applicant = self.env['hr.applicant'].browse(self.env.context.get('default_res_id'))
            applicant_name = applicant.partner_name
            job_position = '(' + applicant.job_id.name + ')'

        else:
            applicant_name = ''
            job_position = ''


        action['context'] = {
            'default_activity_type_id': self.activity_type_id.id,
            'default_res_id': self.env.context.get('default_res_id'),
            'default_res_model': self.env.context.get('default_res_model'),
            'default_name': self.summary  or self.res_name + ' ' + applicant_name + job_position+'-' + self.activity_type_id.name ,
            'default_description': self.note and tools.html2plaintext(self.note).strip() or '',
            'default_activity_ids': [(6, 0, self.ids)],
            'default_activity_type': self.activity_type_id.id,
        }
        return action