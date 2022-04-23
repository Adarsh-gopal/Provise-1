from odoo import api, fields, models, _


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    tech1_interview = fields.Html(tracking=True)
    tech2_interview = fields.Html(tracking=True)
    managerial_interview = fields.Html(tracking=True)
    kanban_state = fields.Selection(selection_add=[('progress', 'Orange'),('hold','Yellow'),('not_intrested','Brown'),('re_schedule','Blue'),('closed','Purple')], default='progress', tracking=True)

    legend_progress = fields.Char(related='stage_id.legend_progress', string='Kanban Progress', readonly=False)
    legend_hold = fields.Char(related='stage_id.legend_hold', string='Kanban Hold', readonly=False)
    legend_not_intrested = fields.Char(related='stage_id.legend_not_intrested', string='Candidate Not Intrested', readonly=False)
    legend_rescheduled = fields.Char(related='stage_id.legend_rescheduled', string='Kanban Rescheduled', readonly=False)
    legend_closed = fields.Char(related='stage_id.legend_closed', string='Kanban closed', readonly=False)

    igc_resume = fields.Binary()

    # interviewer = fields.Many2many('res.users', compute="_get_interviewers_from_calendar", store=True)

    # bg_color = fields.Char(compute="get_bg_color",store=True)

    # @api.depends('kanban_state')
    # def get_bg_color(self):
    #     for rec in self:
    #         if rec.kanban_state == 'normal':
    #             rec.bg_color = '#ffffff'
    #         elif rec.kanban_state == 'done':
    #             rec.bg_color = '#44a148ad'
    #         elif rec.kanban_state == 'blocked':
    #             rec.bg_color = '#dc6865ad'
    #         elif rec.kanban_state == 'progress':
    #             rec.bg_color = '#fea62fa6'
    #         elif rec.kanban_state == 'hold':
    #             rec.bg_color = '#fbe930ab'
    #         elif rec.kanban_state == 'not_intrested':
    #             rec.bg_color = '#a52b2a9e'
    #         elif rec.kanban_state == 're_schedule':
    #             rec.bg_color = '#3776fc99'
    #         else:
    #             rec.bg_color = '#824080a6'

    # @api.depends('meeting_count')
    # def _get_interviewers_from_calendar(self):
    #     for rec in self:
    #         event= self.env['calendar.event'].search([('applicant_id', '=', rec.id)], limit=1, order='id desc')
    #         if event:
    #             rec.interviewer = event.interviewer
    #         else:
    #             rec.interviewer = None


    def update_state(self):
        if self.env.context.get('operation') == 'done':
            applicant = self.write({'kanban_state':'done'})
            if applicant:
                mesg = """ 
                    <div style="background-color:green;color:white;padding:5px;">Selected For Next Stage </div>
                """
                self.message_post(body=mesg)

        if self.env.context.get('operation') == 'not_intrested':
            applicant = self.write({'kanban_state':'not_intrested'})
            if applicant:
                mesg = """ 
                    <div style="background-color:#A52A2A;color:white;padding:5px;">Not Intrested by Candidate </div>
                """
                self.message_post(body=mesg)

        if self.env.context.get('operation') == 'closed':
            applicant = self.write({'kanban_state':'closed'})
            if applicant:
                mesg = """ 
                    <div style="background-color:#800080;color:white;padding:5px;">Closed</div>
                """
                self.message_post(body=mesg)

        if self.env.context.get('operation') == 'progress':
            applicant = self.write({'kanban_state':'progress'})
            if applicant:
                mesg = """ 
                    <div style="background-color:orange;color:white;padding:5px;">In Progress</div>
                """
                self.message_post(body=mesg)

        return True


    def write(self, vals):
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
            vals.update(self._onchange_stage_id_internal(vals.get('stage_id'))['value'])
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'progress'
            for applicant in self:
                vals['last_stage_id'] = applicant.stage_id.id
                res = super(HrApplicant, self).write(vals)
        else:
            res = super(HrApplicant, self).write(vals)
        return res

    def trigger_reason_form(self):
        
        view =self.env.ref('instellars_interview_schedule.kanban_state_reason_form')
        return {
            'name': _('Update Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'kanbanstate.reason',
            'view_id': view.id,
            # 'views': [[self.env.ref('instellars_interview_schedule.kanban_state_reason_form').id, 'form']],
            'view_mode': 'form',
           'target': 'new',
            # 'context': ctx,
        }

         





class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    tech1_interview_feedback_enable = fields.Boolean()
    tech2_interview_feedback_enable = fields.Boolean()
    managerial_interview_feedback_enable = fields.Boolean()

    legend_progress = fields.Char(
        'Orange Kanban Label', default=lambda self: _('In Progress'), translate=True, required=True)
    legend_hold = fields.Char(
        'Yellow Kanban Label', default=lambda self: _('Hold'), translate=True, required=True)
    legend_not_intrested = fields.Char(
        'Brown Kanban Label', default=lambda self: _('Candidate Not Intrested'), translate=True, required=True)

    legend_rescheduled = fields.Char(
        'Blue Kanban Label', default=lambda self: _('Re Scheduled'), translate=True, required=True)
    legend_closed = fields.Char(
        'Purple Kanban Label', default=lambda self: _('Closed'), translate=True, required=True)





