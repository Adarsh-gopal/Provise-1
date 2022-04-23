from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class Project(models.Model):
    _inherit = 'project.project'


    prod_count = fields.Integer(compute='_compute_product_count', string="Product Count")
    duration_days_on_status= fields.Boolean()


    def _compute_product_count(self):
        for rec in self:
            product_data = self.env['product.template'].search([('project_id', '=', rec.id)])
            rec.prod_count = len(product_data)


    def get_product_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attached Products',
            'view_mode': 'kanban,tree,form',
            'res_model': 'product.template',
            'domain': [('project_id', '=', self.id)],
        }

class Task(models.Model):
    _inherit = "project.task"

    effective_duration_days = fields.Float("Days Spent", compute='_compute_effective_duration_days', compute_sudo=True, store=True)
    offsite_count = fields.Integer("Total Off Site", compute ='_compute_delievry_sites',compute_sudo=True, Store=True)
    onsite_count = fields.Integer("Total On Site", compute ='_compute_delievry_sites',compute_sudo=True, Store=True)
    
    tot_hrs_onsite = fields.Float("Total On Site(Hours)", compute ='_compute_delievry_sites',compute_sudo=True, Store=True)
    tot_days_onsite = fields.Float("Total On Site(Days)", compute ='_compute_delievry_sites',compute_sudo=True, Store=True)
    tot_hrs_offsite = fields.Float("Total Off Site(Hours)", compute ='_compute_delievry_sites',compute_sudo=True, Store=True)
    tot_days_offsite = fields.Float("Total Off Site(Days)", compute ='_compute_delievry_sites',compute_sudo=True, Store=True)

    @api.depends('timesheet_ids.duration_days')
    def _compute_effective_duration_days(self):
        for task in self:
            task.effective_duration_days = sum(task.timesheet_ids.mapped('duration_days'))


    @api.depends('timesheet_ids.delivery_site')
    def _compute_delievry_sites(self):
        onsites = []
        tot_hrs_onsite=[]
        tot_days_onsite =[]

        offsites = []
        tot_hrs_offsite=[]
        tot_days_offsite =[]
        for rec in self:
            for line in rec.timesheet_ids:
                if line.delivery_site.id == 1:
                    onsites.append(line.delivery_site)
                    tot_hrs_onsite.append(line.unit_amount)
                    tot_days_onsite.append(line.duration_days)
                if line.delivery_site.id == 2:
                    offsites.append(line.delivery_site)
                    tot_hrs_offsite.append(line.unit_amount)
                    tot_days_offsite.append(line.duration_days)

            rec.onsite_count = len(onsites)
            rec.offsite_count = len(offsites)
            rec.tot_hrs_onsite = sum(tot_hrs_onsite)
            rec.tot_days_onsite = sum(tot_days_onsite)
            rec.tot_hrs_offsite = sum(tot_hrs_offsite)
            rec.tot_days_offsite = sum(tot_days_offsite)


    @api.constrains('timesheet_ids')
    def check_duplicate_date(self):
        for rec in self:
            date_list = []
            for line in rec.timesheet_ids:
                if line.date in date_list:
                    raise ValidationError(_('timesheet updated already for the same date.'))
                else:
                    date_list.append(line.date)