import uuid

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.exceptions import ValidationError
import pdb


class SkillRateCardCreate(models.TransientModel):
    _name = 'skill.rate.card'
    _description = 'It will create new record in skill rate card lines'

    project_id = fields.Many2one('project.project')
    engagement_model = fields.Selection([('staff_augmentation', 'Staff Augmentation'), ('manage_services', 'Manage Services')], string="Engagement Model")
    delivery_site = fields.Many2one('delivery.sites')
    project_skill = fields.Many2one('hr.skill.type')
    duration_of_working = fields.Float('Duration of Working(Hours)')
    domain =  fields.Many2one('hr.employee.domain')
    rate_card_type = fields.Selection([('hourly','Hourly'),('daily','Daily'),('monthly','Monthly')])

    years_of_exp_min = fields.Selection([((str(r)), (str(r))) for r in range(1, 13)],'Years of Experience(Min)')
    years_of_exp_max = fields.Selection([((str(r)), (str(r))) for r in range(1, 13)],'Years of Experience(Max)')
    currency = fields.Many2one('res.currency')
    rate = fields.Float()
    rate_start_date = fields.Date()
    rate_start_end_date =fields.Date()

    @api.model
    def default_get(self, fields):
    	result = super(SkillRateCardCreate, self).default_get(fields)
    	model = self.env.context.get('active_model')
    	if model == 'project.project':
    		project_id = self.env.context.get('active_id')
    		project = self.env['project.project'].sudo().browse(project_id)
    		result['engagement_model'] = project.engagement_model
    		result['project_id'] = project_id

    	return result



    def create_rate_card(self):
        rate_card = self.env['skills.rate.card.lines'].search([('project_id','=',self.project_id.id)])
        if any(rate_card.filtered(lambda l: l.delivery_site.id == self.delivery_site.id and l.project_skill.id == self.project_skill.id and l.years_of_exp_min == self.years_of_exp_min and l.years_of_exp_max == self.years_of_exp_max and l.domain.id == self.domain.id)):
            raise ValidationError(_("Rate Card already present with same values") )
        else:
            self.env['skills.rate.card.lines'].create({
            		'project_id': self.project_id.id,
                    'engagement_model': self.engagement_model,
                    'delivery_site': self.delivery_site.id,
                    'project_skill': self.project_skill.id,
                    'duration_of_working': self.duration_of_working,
                    'domain': self.domain.id,
                    'rate_card_type': self.rate_card_type,
                    'years_of_exp_min': self.years_of_exp_min,
                    'years_of_exp_max': self.years_of_exp_max,
                    'currency': self.currency.id,
                    'rate': self.rate,
                    'rate_start_date': self.rate_start_date,
                    'rate_start_end_date': self.rate_start_end_date,

                })

                
