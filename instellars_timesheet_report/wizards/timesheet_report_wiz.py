from odoo import fields, models, api, _


class TimesheetReportWiz(models.TransientModel):
    _name = 'timesheet.report.wiz'
    _description = 'Timesheet Excel Report'

    from_date = fields.Date('Date From')
    to_date = fields.Date('Date To')
    timesheet_report_line_ids = fields.One2many('timesheet.report.wiz.lines', 'tm_report_id')

    def send_by_mail(self):
        rprt_lin_ids = self.timesheet_report_line_ids.filtered('choose').mapped('id')
        # if rprt_lin_ids:
        attachment = self.env['ir.attachment'].sudo().search([('res_model','=','timesheet.report.wiz.lines'),('res_field','=','timesheet_report'),('res_id','in',rprt_lin_ids)]).mapped('id')


        # attachment = [self.env['ir.attachment'].create({
        #             'name': rec.file_name,
        #             'type': 'binary',
        #             'datas': rec.timesheet_report,
        #             'res_model': 'timesheet.report.wiz.lines',
        #         }).id for rec in self.timesheet_report_line_ids.filtered('choose')]


        template = self.env.ref('instellars_timesheet_report.timesheet_report_mail_template', False)
        # template.write({'attachment_ids':[(6, 0, attachment)]})
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model="timesheet.report.wiz",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            default_attachment_ids =[(6, 0, attachment)],
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


    def unlink_attachment_ids(self):
        rprt_lin_ids = self.timesheet_report_line_ids.filtered('timesheet_report').mapped('id')
        
        attachment = self.env['ir.attachment'].sudo().search([('res_model','=','timesheet.report.wiz.lines'),('res_field','=','timesheet_report'),('res_id','in',rprt_lin_ids)])

        if attachment:
            for each in attachment:
                each.unlink()



class TimeshetReportWizardLine(models.TransientModel):
    _name = 'timesheet.report.wiz.lines'
    _description = 'Timesheet Report Line For Excel report'


    tm_report_id = fields.Many2one('timesheet.report.wiz', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
    project_id = fields.Many2one('project.project',string="Project")
    timesheet_report = fields.Binary('Excel Report')
    file_name = fields.Char('File Name')
    dummy = fields.Char(compute="update_file_name_of_attachment", store=True)
    choose = fields.Boolean(
        default=True)


    @api.depends('timesheet_report','file_name')
    def update_file_name_of_attachment(self):
        for rec in self:
            if rec.timesheet_report and rec.file_name:
                attachment = self.env['ir.attachment'].sudo().search([('res_model','=','timesheet.report.wiz.lines'),('res_field','=','timesheet_report'),('res_id','=',rec.id)])
                attachment.sudo().write({'name':rec.file_name})
