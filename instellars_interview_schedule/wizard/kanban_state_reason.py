import uuid

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.exceptions import ValidationError

from werkzeug.urls import url_encode


class KanbanStateReason(models.TransientModel):
    _name = 'kanbanstate.reason'
    _description = 'get reasons for not candidate rejection and And rescheduling'


    @api.model
    def default_get(self, fields):
        result = super(KanbanStateReason, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        record = self.env['hr.applicant'].sudo().browse(active_id)
        if record:
            result['applicant_id'] = record.id
            result['operation'] = self.env.context.get('operation')
            
        return result 

    # current_state = fields.Char()
    applicant_id = fields.Many2one('hr.applicant')
    reasons = fields.Text('Provide Reason')
    operation = fields.Char()


    def update_reason(self):
        if self.operation == 'reject':
            applicant = self.applicant_id.write({'kanban_state':'blocked'})
            if applicant:
                mesg_data = {
                'reasons':self.reasons,
                }
                mesg = """ 
                    <div style="background-color:red;color:white;padding:5px;">%(reasons)s </div>
                """%(mesg_data)
                self.applicant_id.message_post(body=mesg)

        if self.operation == 'hold':
            applicant = self.applicant_id.write({'kanban_state':'hold'})
            if applicant:
                mesg_data = {
                'reasons':self.reasons,
                }
                mesg = """ 
                    <div style="background-color:yellow;color:black;padding:5px;">%(reasons)s </div>
                """%(mesg_data)
                self.applicant_id.message_post(body=mesg)

        if self.operation == 're_schedule':
            applicant = self.applicant_id.write({'kanban_state':'re_schedule'})
            if applicant:
                mesg_data = {
                'reasons':self.reasons,
                }
                mesg = """ 
                    <div style="background-color:blue;color:white;padding:5px;">%(reasons)s </div>
                """%(mesg_data)
                self.applicant_id.message_post(body=mesg)


        return True

