from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    #need aproval checkbox at stages to check weather that stage needs aproval
    need_approval = fields.Boolean()



class Applicant(models.Model):
    _inherit = "hr.applicant"

    #list of approvers at each application
    approver = fields.Many2many('res.users')
    # current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user.id)
    is_user_approver = fields.Boolean(string="is he approver?", compute='get_approver_status')

    stage_approved = fields.Boolean(string="is approved?", store=True)

    def get_approver_status(self):
        for rec in self:
            user = self.env['res.users'].search([('name', '=', self.env.user.name)])
            if user.has_group('kanban_stage_change_vallidation.allow_adding_approvers'):
                rec.is_user_approver = True
            else:
                rec.is_user_approver = False

    # @api.depends('stage_id')
    # def update_approved(self):
    #     for rec in self:
    #         need_approval_sequence = self.env['hr.recruitment.stage'].search([('need_approval','=',True)],limit=1).sequence
    #         if rec.stage_id.need_approval:
    #             rec.stage_approved = True
    #         elif  rec.stage_id.sequence > need_approval_sequence:
    #             # if rec.stage_approved != False:
    #             #     raise UserError(_('Approval is pending!! Please Refresh the page for changes!'))
    #             rec.stage_approved = None
    #         else:
    #             rec.stage_approved = False

        # applicant = rec.write({'stage_approved':True})
        # if applicant:
        #     # applicant.write({'stage_approved':True})
        #     return True



    @api.onchange('stage_id')
    def check_approver(self):
        for rec in self:
            if rec.stage_id.id == 1 or rec.approver:
                need_approval_sequence = self.env['hr.recruitment.stage'].search([('need_approval','=',True)],limit=1).sequence
                if rec.stage_id.need_approval:
                    if not self.env.uid in rec.approver.ids:
                        raise UserError(_('You are not supposed to move to this stage!. Please Refresh the page for changes!'))
                    else:
                        # approve = rec.write({'stage_approved': True})
                        rec.stage_approved = True
                        # self.update_approved(rec)


                if rec.stage_id.sequence > need_approval_sequence:
                    if rec.stage_approved != True:
                        raise UserError(_('Approval is pending!! Please Refresh the page for changes!'))
            else:
                raise UserError(_('Approver is not set!'))



    # @api.onchange('stage_id')
    # def onchange_stage_id_kanban(self):
    #     vals = self.get_bolean_true(self.stage_id.id)
    #     if vals['value'].get('stage_approved'):
    #         self.stage_approved = vals['value']['stage_approved']

    # def get_bolean_true(self, stage_id):
    #     if not stage_id:
    #         return {'value': {}}
    #     stage = self.env['hr.recruitment.stage'].browse(stage_id)
    #     if stage.need_approval:
    #         return {'value': {'stage_approved': True}}
    #     return {'value': {'stage_approved': False}}



                    # return {
                    #           'type': 'ir.actions.client',
                    #           'tag': 'reload',
                    #       }
        #   current_stage_squence = lead.stage_id.sequence + 1
        #   if current_stage_squence <= 7:
        #       next_stage_stage = self.env['crm.stage'].search([('sequence', '=', current_stage_squence)])
        #       # print(next_stage_stage,'**********************************')
        #       lead.write({'stage_id': next_stage_stage.id, **values})
        # # self._rebuild_pls_frequency_table_threshold()
        # return True
