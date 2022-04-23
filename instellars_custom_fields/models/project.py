from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Project(models.Model):
    _inherit = 'project.project'

    #projects star and end details
    date_start = fields.Date('Project Start Date')
    date_end = fields.Date('Project End Date')

    related_products = fields.Many2many('product.template',compute='_compute_product_ids',)

    engagement_model = fields.Selection([('staff_augmentation', 'Staff Augmentation'), ('manage_services', 'Manage Services')], string="Engagement Model")
    project_extension = fields.Selection([('extendable', 'Extendable'), ('not_extendable', 'Not Extendable')], string="Project Extension")
    no_of_resource_in_the_project = fields.Integer()
    project_location = fields.Many2one('hr.location')

    skills_rate_card_line_items = fields.One2many('skills.rate.card.lines', 'project_id', string="Rate Card Line Items")

    def _compute_product_ids(self):
        for rec in self:
            product_data = self.env['product.template'].search([('project_id', '=', rec.id)])
            rec.related_products =[(6,0,product_data.ids)]


class SillSetRateCard(models.Model):
    _name = 'skills.rate.card.lines'
    _description = "skills rate card lines"


    project_id = fields.Many2one('project.project', required=True)
    engagement_model = fields.Selection([('staff_augmentation', 'Staff Augmentation'), ('manage_services', 'Manage Services')], string="Engagement Model")
    delivery_site = fields.Many2one('delivery.sites')
    project_skill = fields.Many2one('hr.skill.type')
    duration_of_working = fields.Float()
    domain =  fields.Many2one('hr.employee.domain')
    rate_card_type = fields.Selection([('hourly','Hourly'),('daily','Daily'),('monthly','Monthly')])

    # no_of_years_of_exp_min = fields.Many2one('experience.range', 'No of Years of Experience (Min)')
    # no_of_years_of_exp_max = fields.Many2one('experience.range', 'No of Years of Experience (Max)')
    years_of_exp_min = fields.Selection([((str(r)), (str(r))) for r in range(1, 13)],'Years of Experience(Min)')
    years_of_exp_max = fields.Selection([((str(r)), (str(r))) for r in range(1, 13)],'years of Experience(Max)')
    currency = fields.Many2one('res.currency')
    rate = fields.Float()
    rate_start_date = fields.Date()
    rate_start_end_date =fields.Date()


        

