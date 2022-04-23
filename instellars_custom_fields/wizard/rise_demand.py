import uuid

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.exceptions import ValidationError


class CrmLeadForm(models.TransientModel):
    _name = 'project.demand'
    _description = 'Transient model for demand generation'

    #fields for creating demands
    certification_type = fields.Many2one('hr.skill.type', string="Project Skill")
    certification = fields.Many2many('hr.skill', string="Skill")
    domain =  fields.Many2one('hr.employee.domain')
    # experience_min_max = fields.Many2one('experience.range', string="Experience(min-max)")
    years_of_exp_min = fields.Selection([((str(r)), (str(r))) for r in range(1, 13)],'Years of Experience(Min)')
    years_of_exp_max = fields.Selection([((str(r)), (str(r))) for r in range(1, 13)],'Years of Experience(Max)')
    demand_closed_date = fields.Date()
    no_of_resource_required = fields.Integer(required=True)
    job_description = fields.Binary()
    delivery_site = fields.Many2one('delivery.sites', string="Delivery Site")
    project_id = fields.Many2one('project.project')

    #for product_attached
    product_id = fields.Many2one('product.product', domain=[('type', '=', 'service'), ('invoice_policy', '=', 'delivery'), ('service_type', '=', 'timesheet')], string="Service", help="Product of the sales order item. Must be a service invoiced based on timesheets on tasks.")

    @api.model
    def default_get(self, fields):
        result = super(CrmLeadForm, self).default_get(fields)
        model = self.env.context.get('active_model')
        # if model == 'project.project':
        project_id = self.env.context.get('active_id')
        # project = self.env['project.project'].sudo().browse(project_id)

        result['project_id'] = project_id

        return result

    # @api.onchange('years_of_exp_max')
    # def vallidate_experience_range(self):
    #     if int(self.years_of_exp_max) <= int(self.years_of_exp_min):
    #         raise ValidationError(_("maximum experience should greater than minimum experience"))

    def raise_demand(self):
        # project_name = self.project_id.name
        for cr in range(self.no_of_resource_required):
            self.env['demands'].create({
            		'type': 'demand',
                    # 'is_demand': True,
            		'name': self.project_id.name,
                    'certification_type': self.certification_type.id,
                    'certification': [(6, 0, self.certification.ids)],
                    'domain':self.domain.id,
                    'years_of_exp_min': self.years_of_exp_min,
                    'years_of_exp_max': self.years_of_exp_max,
                    'delivery_site':self.delivery_site.id,
                    'partner_id':self.project_id.partner_id.id,
                    'product_id':self.product_id.id,
                    'demand_closed_date':self.demand_closed_date,
                    
                    'project_id': self.project_id.id,
                    'job_description': self.job_description,

                })

