from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import date 
from dateutil import relativedelta

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    day =  fields.Char(compute="get_day_from_date")
    status = fields.Selection([('full_day','Full Day'),('half_day','Half Day'),('absent','Absent'),('weekend','Weekend'),('public_holiday','Public HoliDay'),('comp_off','Comp Off'),('business_travel','Business Travel')])
    delivery_site = fields.Many2one('delivery.sites')
    # delivery_site = fields.Selection([('onsite','Onsite'),('offsite','Offsite')])
    duration_days = fields.Float(compute="get_duration_days",string='Duration(Days)',store=True, group_operator='sum')

    # onsite = fields.Integer("On Site", compute ='_compute_delievry_sites',compute_sudo=True, Store=True)
    # offsite = fields.Integer("Off Site", compute ='_compute_delievry_sites',compute_sudo=True, Store=True)
    
    hrs_onsite = fields.Float("On Site Duration(Hours)", compute ='_compute_delievry_sites',compute_sudo=True, store=True, group_operator='sum')
    days_onsite = fields.Float("On Site Duration(Days)", compute ='_compute_delievry_sites',compute_sudo=True,  store=True, group_operator='sum')
    hrs_offsite = fields.Float("Off Site Duration(Hours)", compute ='_compute_delievry_sites',compute_sudo=True,  store=True, group_operator='sum')
    days_offsite = fields.Float("Off Site Duration(Days)", compute ='_compute_delievry_sites',compute_sudo=True,  store=True, group_operator='sum')

    @api.depends('delivery_site','unit_amount','duration_days')
    def _compute_delievry_sites(self):
        for rec in self:
            if rec.delivery_site.id == 1:
                rec.hrs_onsite = rec.unit_amount
                rec.days_onsite = rec.duration_days
                rec.hrs_offsite = 0
                rec.days_offsite = 0
            elif rec.delivery_site.id == 2:
                rec.hrs_onsite = 0
                rec.days_onsite = 0
                rec.hrs_offsite = rec.unit_amount
                rec.days_offsite = rec.duration_days
            else:
                rec.hrs_onsite = 0
                rec.days_onsite = 0
                rec.hrs_offsite = 0
                rec.days_offsite = 0



    @api.depends('status','project_id','unit_amount')
    def get_duration_days(self):
        for rec in self:
            if rec.project_id.duration_days_on_status:
                if rec.status == 'full_day':
                    rec.duration_days = 1
                elif rec.status == 'half_day':
                    rec.duration_days = 0.5
                elif rec.status == 'absent':
                    rec.duration_days = 0
                elif rec.status == 'weekend':
                    rec.duration_days = 0
                elif rec.status == 'public_holiday':
                    rec.duration_days = 0
                elif rec.status == 'comp_off':
                    rec.duration_days = 1
                else:
                    rec.duration_days = 0
            else:
                if rec.unit_amount >= 5:
                    rec.duration_days = 1
                if rec.unit_amount < 5:
                    rec.duration_days = 0.5
                if rec.unit_amount <= 0:
                    rec.duration_days = 0



    @api.depends('date')
    def get_day_from_date(self):
        for rec in self:
            rec.day = rec.date.strftime('%A')