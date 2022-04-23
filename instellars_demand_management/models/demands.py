import logging
from psycopg2 import sql, extras
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _

from odoo.exceptions import UserError, AccessError
from odoo.addons.phone_validation.tools import phone_validation

from . import demand_stage

from odoo.fields import Date



class Demands(models.Model):
    _name = "demands"
    _description = "Demands Management"
    _order = "priority desc, id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']


    def _default_stage_id(self):
        state = self.env.ref('instellars_demand_management.stage_demand1', raise_if_not_found=False)
        return state if state and state.id else False


    name = fields.Char('Demands', required=True, index=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_name = fields.Char("Company Name", tracking=20, index=True)
    email_from = fields.Char('Email', help="Email address of the contact", tracking=40, index=True)
    kanban_state = fields.Selection([('grey', 'No next activity planned'), ('red', 'Next activity late'), ('green', 'Next activity is planned')],
        string='Kanban State', compute='_compute_kanban_state')
    description = fields.Text('Notes')
    priority = fields.Selection(demand_stage.AVAILABLE_PRIORITIES, string='Priority', index=True, default=demand_stage.AVAILABLE_PRIORITIES[0][0])
    type = fields.Selection([('demand', 'Demand'), ('opportunity', 'Opportunity')], index=True, required=True, tracking=15,
    default=lambda self: 'demand' if self.env['res.users'].has_group('instellars_demand_management.group_use_demand') else 'opportunity',
    help="Type is used to separate Leads and Opportunities")
    stage_id = fields.Many2one('demand.stage', string='Stage', ondelete='restrict', tracking=True, index=True, copy=False,
        group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())
    is_won = fields.Boolean(related='stage_id.is_won')
    phone = fields.Char('Phone', tracking=50)
    mobile = fields.Char('Mobile')
    contact_name = fields.Char('Contact Name', tracking=30)
    website = fields.Char('Website', index=True, help="Website of the contact")
    user_id = fields.Many2one('res.users', string='Manager', index=True, tracking=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    color = fields.Integer('Color Index', default=0)
    user_email = fields.Char('User Email', related='user_id.email', readonly=True)
    user_login = fields.Char('User Login', related='user_id.login', readonly=True)


    # Fields for address, due to separation from crm and res.partner
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    lang_id = fields.Many2one('res.lang', string='Language', help="Language of the demands.")


    project_id = fields.Many2one('project.project' ,string="Project Name",tracking=True)
    certification_type = fields.Many2one('hr.skill.type', string="Skill Type",tracking=True)
    certification = fields.Many2many('hr.skill', string="Skill",tracking=True)
    # experience_min_max = fields.Many2one('experience.range', string="Experience(min-max)")
    years_of_exp_min = fields.Selection([((str(r)), (str(r))) for r in range(1, 13)],'Years of Experience(Min)',tracking=True)
    years_of_exp_max = fields.Selection([((str(r)), (str(r))) for r in range(1, 13)],'Years of Experience(Max)',tracking=True)
    delivery_site = fields.Many2one('delivery.sites', string="Delivery Site",tracking=True)
    demand_closed_date = fields.Date(tracking=True)
    employee_assigned = fields.Many2one('hr.employee',tracking=True)
    employee_assigned_date = fields.Date(tracking=True)
    job_description = fields.Binary('Job Description',tracking=True)
    domain =  fields.Many2one('hr.employee.domain',tracking=True)
    # is_demand =  fields.Boolean(tracking=True)
    product_id = fields.Many2one('product.product', domain=[('type', '=', 'service'), ('invoice_policy', '=', 'delivery'), ('service_type', '=', 'timesheet')], string="Service",  help="Product of the sales order item. Must be a service invoiced based on timesheets on tasks.",tracking=True)
    demand_status = fields.Selection([('open','Open'),('close','Close')], compute="get_demand_status", store=True,tracking=True)
    date_closed = fields.Datetime('Closed Date', readonly=True, copy=False,tracking=True)

    #coneverting string to foloat for filter purpose

    exp_min_val_float =fields.Float(compute="get_float_value_exp", store=True,tracking=True)
    exp_max_val_float =fields.Float(compute="get_float_value_exp", store=True,tracking=True)


    #for calculation purpose
    is_employee_assigned = fields.Boolean( store=True,tracking=True)

    date_open = fields.Datetime('Assignation Date', readonly=True, default=fields.Datetime.now, tracking=True)
    day_open = fields.Float(compute='_compute_day_open', string='Days to Assign', store=True,tracking=True)
    day_close = fields.Float(compute='_compute_day_close', string='Days to Close', store=True,tracking=True)
    date_last_stage_update = fields.Datetime(string='Last Stage Update', index=True, default=fields.Datetime.now,tracking=True)
    date_conversion = fields.Datetime('Conversion Date', readonly=True,tracking=True)

    @api.onchange('project_id')
    def get_related_product(self):
        for rec in self:
            if rec.project_id:
                product = self.env['product.product'].search([('type', '=', 'service'), ('invoice_policy', '=', 'delivery'), ('service_type', '=', 'timesheet'),('project_id','=',rec.project_id.id)],limit=1)
                if product:
                    rec.product_id= product.id
                else:
                    rec.product_id = None

    @api.depends('date_open')
    def _compute_day_open(self):
        """ Compute difference between create date and open date """
        leads = self.filtered(lambda l: l.date_open and l.create_date)
        others = self - leads
        others.day_open = None
        for lead in leads:
            date_create = fields.Datetime.from_string(lead.create_date)
            date_open = fields.Datetime.from_string(lead.date_open)
            lead.day_open = abs((date_open - date_create).days)

    @api.depends('date_closed')
    def _compute_day_close(self):
        """ Compute difference between current date and log date """
        leads = self.filtered(lambda l: l.date_closed and l.create_date)
        others = self - leads
        others.day_close = None
        for lead in leads:
            date_create = fields.Datetime.from_string(lead.create_date)
            date_close = fields.Datetime.from_string(lead.date_closed)
            lead.day_close = abs((date_close - date_create).days)

    def write(self, vals):
        res = super(Demands, self).write(vals)
        if vals.get('employee_assigned'):
            self.change_employee_status()
        return res

    def change_employee_status(self):
        for rec in self:
            if rec.employee_assigned:
                rec.is_employee_assigned = True
                emp = self.env['hr.employee'].search([('id', '=', rec.employee_assigned.id)])
                emp.write({'employee_status':2,'project_id':rec.project_id.id})

    @api.depends('years_of_exp_min','years_of_exp_max')
    def get_float_value_exp(self):
        for rec in self:
            rec.exp_min_val_float = float(rec.years_of_exp_min)
            rec.exp_max_val_float = float(rec.years_of_exp_max)



    @api.depends('demand_closed_date','employee_assigned')
    def get_demand_status(self):
        for rec in self:
            if rec.demand_closed_date :
                if rec.demand_closed_date < Date.today() or rec.employee_assigned:
                    rec.demand_status = 'close'
                else:
                    rec.demand_status = 'open'
            else:
                rec.demand_status = None

    def action_set_lost(self, **additional_values):
        """ Lost semantic: probability = 0 or active = False """
        result = self.write({'active': False})
        return result



    def _onchange_partner_id_values(self, partner_id):
        """ returns the new values when partner_id has changed """
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)

            partner_name = partner.parent_id.name
            if not partner_name and partner.is_company:
                partner_name = partner.name

            return {
                'partner_name': partner_name,
                'contact_name': partner.name if not partner.is_company else False,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id.id,
                'country_id': partner.country_id.id,
                'email_from': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'zip': partner.zip,
                'website': partner.website,
            }
        return {}

    def _stage_find(self,  domain=None, order='sequence'):
        if domain:
            search_domain = list(domain)
        # perform search, return the first found
        return self.env['demand.stage'].search(search_domain, order=order, limit=1)

    def action_set_won(self):
        """ Won semantic: probability = 100 (active untouched) """
        for demand in self:
            stage_id = demand._stage_find(domain=[('is_won', '=', True)])
            demand.write({'stage_id': stage_id.id})
        return True

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        values = self._onchange_partner_id_values(self.partner_id.id if self.partner_id else False)
        self.update(values)




    def _read_group_stage_ids(self, stages, domain, order):
        # return [key for key, val in type(self).state.many2one]
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _compute_kanban_state(self):
        today = date.today()
        for demand in self:
            kanban_state = 'grey'
            if demand.activity_date_deadline:
                demand_date = fields.Date.from_string(demand.activity_date_deadline)
                if demand_date >= today:
                    kanban_state = 'green'
                else:
                    kanban_state = 'red'
            demand.kanban_state = kanban_state


    @api.model
    def create(self, vals):
        # set up context used to find the lead's Sales Team which is needed
        # to correctly set the default stage_id
        context = dict(self._context or {})
        if vals.get('type') and not self._context.get('default_type'):
            context['default_type'] = vals.get('type')

        if vals.get('user_id') and 'date_open' not in vals:
            vals['date_open'] = fields.Datetime.now()

        partner_id = vals.get('partner_id') or context.get('default_partner_id')
        onchange_values = self._onchange_partner_id_values(partner_id)
        onchange_values.update(vals)  # we don't want to overwrite any existing key
        vals = onchange_values

        result = super(Demands, self.with_context(context)).create(vals)
        # Compute new probability for each lead separately
        return result


    def _convert_opportunity_data(self, customer, team_id=False):
        """ Extract the data from a lead to create the opportunity
            :param customer : res.partner record
            :param team_id : identifier of the Sales Team to determine the stage
        """
        value = {
            'name': self.name,
            'partner_id': customer.id if customer else False,
            'type': 'opportunity',
            'date_open': fields.Datetime.now(),
            'email_from': customer and customer.email or self.email_from,
            'phone': customer and customer.phone or self.phone,
            'date_conversion': fields.Datetime.now(),
        }
        if not self.stage_id:
            stage = self._default_stage_id(team_id=team_id)
            value['stage_id'] = stage.id
        return value

    def convert_opportunity(self, partner_id, user_ids=False):
        customer = False
        if partner_id:
            customer = self.env['res.partner'].browse(partner_id)
        for demand in self:
            if not demand.active:
                continue
            vals = demand._convert_opportunity_data(customer)
            print(vals,'*****************************************')
            demand.write(vals)

        return True

    def redirect_demand_opportunity_view(self):
        self.ensure_one()
        return {
            'name': _('Demand or Opportunity'),
            'view_mode': 'form',
            'res_model': 'demands',
            'domain': [('type', '=', self.type)],
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'default_type': self.type}
        }

    #sale management related fields and customizations
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    sale_amount_total = fields.Monetary(compute='_compute_sale_data', string="Sum of Orders", help="Untaxed Total of Confirmed Orders", currency_field='company_currency')
    quotation_count = fields.Integer(compute='_compute_sale_data', string="Number of Quotations")
    sale_order_count = fields.Integer(compute='_compute_sale_data', string="Number of Sale Orders")
    order_ids = fields.One2many('sale.order', 'demands_id', string='Orders')

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order', 'order_ids.company_id')
    def _compute_sale_data(self):
        for demand in self:
            total = 0.0
            quotation_cnt = 0
            sale_order_cnt = 0
            company_currency = demand.company_currency or self.env.company.currency_id
            for order in demand.order_ids:
                if order.state in ('draft', 'sent'):
                    quotation_cnt += 1
                if order.state not in ('draft', 'sent', 'cancel'):
                    sale_order_cnt += 1
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id, order.date_order or fields.Date.today())
            demand.sale_amount_total = total
            demand.quotation_count = quotation_cnt
            demand.sale_order_count = sale_order_cnt

    @api.model
    def retrieve_sales_dashboard(self):
        res = super(Demands, self).retrieve_sales_dashboard()
        date_today = fields.Date.from_string(fields.Date.context_today(self))

        res['invoiced'] = {
            'this_month': 0,
            'last_month': 0,
        }
        account_invoice_domain = [
            ('state', '=', 'posted'),
            ('invoice_user_id', '=', self.env.uid),
            ('invoice_date', '>=', date_today.replace(day=1) - relativedelta(months=+1)),
            ('type', 'in', ['out_invoice', 'out_refund'])
        ]

        invoice_data = self.env['account.move'].search_read(account_invoice_domain, ['invoice_date', 'amount_untaxed', 'type'])

        for invoice in invoice_data:
            if invoice['invoice_date']:
                invoice_date = fields.Date.from_string(invoice['invoice_date'])
                sign = 1 if invoice['type'] == 'out_invoice' else -1
                if invoice_date <= date_today and invoice_date >= date_today.replace(day=1):
                    res['invoiced']['this_month'] += sign * invoice['amount_untaxed']
                elif invoice_date < date_today.replace(day=1) and invoice_date >= date_today.replace(day=1) - relativedelta(months=+1):
                    res['invoiced']['last_month'] += sign * invoice['amount_untaxed']

        res['invoiced']['target'] = self.env.user.target_sales_invoiced
        return res

    def action_sale_quotations_new(self):
        if not self.partner_id:
            return self.env.ref("instellars_demand_management.demand_quotation_partner_action").read()[0]
        else:
            return self.action_new_quotation()

    def action_new_quotation(self):
        action = self.env.ref("instellars_demand_management.demand_sale_action_quotations_new").read()[0]
        action['context'] = {
            'search_default_demands_id': self.id,
            'default_demands_id': self.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_origin': self.name,
            'default_name': self.name,
            'default_project_id': self.project_id.id,
            'default_order_line' :[(0, None, {'product_id': self.product_id.id,
                                              'resource_name':self.employee_assigned.id,
                                              'name':self.product_id.name,
                                              'product_uom':self.product_id.uom_id.id,
                                              'product_uom_qty':1.000,
                                              'price_unit':self.product_id.list_price})]
        }
        return action

    def action_view_sale_quotation(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['context'] = {
            'search_default_draft': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id), ('state', 'in', ['draft', 'sent'])]
        quotations = self.mapped('order_ids').filtered(lambda l: l.state in ('draft', 'sent'))
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action

    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders').read()[0]
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id,
        }
        action['domain'] = [('opportunity_id', '=', self.id), ('state', 'not in', ('draft', 'sent', 'cancel'))]
        orders = self.mapped('order_ids').filtered(lambda l: l.state not in ('draft', 'sent', 'cancel'))
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action


    #profile matching for employeee
    match_count = fields.Integer(compute='_compute_match_count', string="match Count")


    def _compute_match_count(self):
        for rec in self:
            employee_data = self.env['hr.employee'].search([('employee_status', '=', 1),('domain','!=',False),('domain','=',rec.domain.id),
                ('employee_skill_ids.skill_type_id','=',rec.certification_type.id),('employee_skill_ids.skill_type_id','!=',False),
                ('employee_skill_ids.skill_id','in',rec.certification.ids),('employee_skill_ids.skill_id','!=',False),
                ('relevant_yrs_of_exp_till_date','>=',float(self.years_of_exp_min)),('relevant_yrs_of_exp_till_date','<=',float(self.years_of_exp_max)),
            ('relevant_yrs_of_exp_till_date','!=',None)])
            rec.match_count = len(employee_data)



    def get_employee_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Matched Employees',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee',
            'domain': [('employee_status', '=', 1),('domain','!=',False),('domain','=',self.domain.id),
            ('employee_skill_ids.skill_type_id','=',self.certification_type.id),('employee_skill_ids.skill_type_id','!=',False),
            ('employee_skill_ids.skill_id','in',self.certification.ids),('employee_skill_ids.skill_id','!=',False),
            ('relevant_yrs_of_exp_till_date','>=',float(self.years_of_exp_min)),('relevant_yrs_of_exp_till_date','<=',float(self.years_of_exp_max)),
            ('relevant_yrs_of_exp_till_date','!=',None)],
            'context': "{'create': False}"
           
        }

    # def write(self, vals):
    #     # stage change:
    #     if 'stage_id' in vals:
    #         vals['date_last_stage_update'] = fields.Datetime.now()
    #         stage_id = self.env['crm.stage'].browse(vals['stage_id'])
    #         if stage_id.is_won:
    #             vals.update({'probability': 100})
    #     # Only write the 'date_open' if no salesperson was assigned.
    #     if vals.get('user_id') and 'date_open' not in vals and not self.mapped('user_id'):
    #         vals['date_open'] = fields.Datetime.now()
    #     # stage change with new stage: update probability and date_closed
    #     if vals.get('probability', 0) >= 100 or not vals.get('active', True):
    #         vals['date_closed'] = fields.Datetime.now()
    #     elif 'probability' in vals:
    #         vals['date_closed'] = False
    #     if vals.get('user_id') and 'date_open' not in vals:
    #         vals['date_open'] = fields.Datetime.now()

    #     write_result = super(Lead, self).write(vals)
    #     # Compute new automated_probability (and, eventually, probability) for each lead separately
    #     self._write_probability(vals)

    #     return write_result


