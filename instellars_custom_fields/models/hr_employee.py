from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import date ,datetime
from dateutil import relativedelta
import re

class HrEmployeeBase(models.AbstractModel):
	_inherit = "hr.employee.base"

	#personnel details block
	blood_group = fields.Selection([('O+', 'O+'), ('O-', 'O-'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-')], string='Blood Group')
	father_name = fields.Char('Father Name')
	mother_name = fields.Char('Mother Name')
	skype_id = fields.Char()
	employee_status= fields.Many2one('employee.status')

	#empoyment offered details
	offer_date = fields.Date()
	date_of_joining = fields.Date()

	offered_salary = fields.Float()
	remarks = fields.Text()
	hire_type = fields.Selection([('internal','Internal'),('external','External')])
	title = fields.Many2one('res.partner.title')

	#field will store Employee photo for thier Employee ID card
	# photo_for_id =fields.Binary(string="Photo for ID")
	universal_account_number = fields.Char(string="UAN")
	provident_fund = fields.Char(string="PF Number")
	esi_number = fields.Char(string="ESI Number")

	# #pan details of the employee
	pan_no = fields.Char(string="PAN No.")
	# pan_doc = fields.Binary(string="PAN Doc")

	# aadhar_doc = fields.Binary(string="Aadhar Doc")

	# certificate_of_fitness = fields.Binary(string="Certificate of Fitness")

	# #Education related fields
	employee_degree = fields.Many2many('hr.employee.degree')
	degree_type = fields.Many2one('hr.employee.degree.type', "Degree Type")
	division = fields.Many2one('hr.employee.degree.division', "Division")
	year_of_pass = fields.Selection([((str(num)), (str(num))) for num in range(1900, (datetime.now().year)+1)], 'Year of Pass')
	# year_of_pass = fields.Date("Year of Pass")
	university_name = fields.Char("University Name")
	percentage = fields.Float("Percentage %")

	# #emergency contact details
	relation_with_employee = fields.Char(string="Relation")
	emergency_contact_city = fields.Char(string="City")
	emergency_contact_state = fields.Many2one("res.country.state")
	emergency_contact_country = fields.Many2one("res.country")

	# #skills management
	# fresher = fields.Boolean('Fresher')
	# experienced = fields.Boolean('Experienced')
	experience_level = fields.Selection([('fresher', 'Fresher'), ('experienced', 'Experienced')], string="Experience Level",default='fresher')
	domain = fields.Many2one('hr.employee.domain')
	# last_working_company = fields.Many2one('res.partner')
	last_working_company = fields.Char()
	last_drawn_salary = fields.Integer("Last Drawn Salary")
	last_company_department = fields.Char("Last Company Department")
	last_company_designation = fields.Char("Last Company Designation")
	last_working_day = fields.Date("Last Working Day")
	start_date_of_career = fields.Date("Start Date of Career") 
	last_company_employeed_code = fields.Char("Last Company Employee Code")
	reason_for_leaving = fields.Text("Reason for Leaving")
	total_years_of_experience = fields.Float("Total Years of Experience")
	relevant_years_of_experience = fields.Float("Relevant Years of Experience")
	relevant_yrs_of_exp_till_date = fields.Float("Relevant Years of Experience Till Date", store=True)
	total_yrs_of_exp_till_date = fields.Float("Total Years of Experience Till Date", store=True)



	# #experienced documents
	# previous_company_salary_slip = fields.Binary("Previous Company Salary Slip (3 Months)")
	# last_company_releiving_letter =fields.Binary("Last Company releiving letter")
	# last_company_experience_letter =fields.Binary("Last Company experience letter")
	# last_company_offer_letter =fields.Binary("Last Company offer letter")


	# #present and permanent address

	street_present = fields.Char(store=True)
	street2_present = fields.Char(store=True)
	zip_present = fields.Char(store=True, change_default=True)
	city_present = fields.Char(store=True)
	state_id_present = fields.Many2one("res.country.state",store=True,  ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	country_id_present = fields.Many2one('res.country', store=True,  ondelete='restrict')


	street_permanent = fields.Char(store=True)
	street2_permanent = fields.Char(store=True)
	zip_permanent = fields.Char(store=True, change_default=True)
	city_permanent = fields.Char(store=True)
	state_id_permanent = fields.Many2one("res.country.state",store=True, ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	country_id_permanent = fields.Many2one('res.country',store=True, ondelete='restrict')

	# #off board 
	offboarding_type = fields.Selection([('exit_from_company', 'Exit From Company'), ('offboard_from_current_project', 'Offboard From Current Project')], string="Select Type")
	resigned_date = fields.Date()
	get_last_working_day = fields.Selection([('system', 'System'),('custom', 'Custom')], string="Get Last Working Day")
	# notice_period = fields.Date(string="Notice Period(System Generate 2 months)")
	reason_for_resigning = fields.Many2one('hr.resign.reason')
	informed_client = fields.Selection([('yes','Yes'),('no','No')])
	notice_period_adjustable = fields.Char()

	# #offboard_from project
	offboard_date_from_current_project = fields.Date()
	reasons_for_offboarding = fields.Many2one('hr.offboarding.reason')
	off_board_type = fields.Selection([('bench', 'Bench')], string="Off Board Type")

	project_id = fields.Many2one('project.project', 'Project Name')



	# #off boarding details
	off_board = fields.Boolean()
	registration_number = fields.Char("	Registration Number of the Employee",copy=False, default=lambda self: _('New'))

	#probation and confirmation fields
	confirmation_types = fields.Selection([('probation', 'Probation'),('pip', 'PIP'),('confirmed', 'Confirmed')], string="Confirmation Type")
	pip_duration = fields.Selection([('1_month', '1 Month'),('2_month', '2 Month'),('3_month', '3 Month')], string="PIP Duration")
	confirmation_date = fields.Date(string='Confirmation Date',store=True)

	confirmation_ref = fields.Char('Confirmation Reference', store=True,tracking=True)
	pip_ref = fields.Char('PIP Reference', store=True,tracking=True)
	relieving_letter_ref = fields.Char('Relieving Letter Reference', store=True,tracking=True)
	sign_request_count_probationary = fields.Integer( store=True)


class HrEmployee(models.Model):
	_inherit = "hr.employee"

	#personnel details block
	blood_group = fields.Selection([('O+', 'O+'), ('O-', 'O-'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-')], string='Blood Group')
	father_name = fields.Char('Father Name')
	mother_name = fields.Char('Mother Name')
	skype_id = fields.Char()
	employee_status= fields.Many2one('employee.status')

	#empoyment offered details
	offer_date = fields.Date()
	date_of_joining = fields.Date()

	offered_salary = fields.Float()
	remarks = fields.Text()
	hire_type = fields.Selection([('internal','Internal'),('external','External')])
	title = fields.Many2one('res.partner.title')

	#field will store Employee photo for thier Employee ID card
	photo_for_id =fields.Binary(string="Photo for ID")
	universal_account_number = fields.Char(string="UAN")
	provident_fund = fields.Char(string="PF Number")
	esi_number = fields.Char(string="ESI Number")

	#pan details of the employee
	pan_no = fields.Char(string="PAN No.")
	pan_doc = fields.Binary(string="PAN Doc")

	aadhar_doc = fields.Binary(string="Aadhar Doc")

	certificate_of_fitness = fields.Binary(string="Certificate of Fitness")

	#Education related fields
	employee_degree = fields.Many2many('hr.employee.degree')
	degree_type = fields.Many2one('hr.employee.degree.type', "Degree Type")
	division = fields.Many2one('hr.employee.degree.division', "Division")
	year_of_pass = fields.Selection([((str(num)), (str(num))) for num in range(1900, (datetime.now().year)+1)], 'Year of Pass')
	# year_of_pass = fields.Date("Year of Pass")
	university_name = fields.Char("University Name")
	percentage = fields.Float("Percentage %")

	#emergency contact details
	relation_with_employee = fields.Char(string="Relation")
	emergency_contact_city = fields.Char(string="City")
	emergency_contact_state = fields.Many2one("res.country.state")
	emergency_contact_country = fields.Many2one("res.country")

	#skills management
	# fresher = fields.Boolean('Fresher')
	# experienced = fields.Boolean('Experienced')
	experience_level = fields.Selection([('fresher', 'Fresher'), ('experienced', 'Experienced')], string="Experience Level",default='fresher')
	domain = fields.Many2one('hr.employee.domain')
	# last_working_company = fields.Many2one('res.partner')
	last_working_company = fields.Char()
	last_drawn_salary = fields.Integer("Last Drawn Salary")
	last_company_department = fields.Char("Last Company Department")
	last_company_designation = fields.Char("Last Company Designation")
	last_working_day = fields.Date("Last Working Day")
	start_date_of_career = fields.Date("Start Date of Career") 
	last_company_employeed_code = fields.Char("Last Company Employee Code")
	reason_for_leaving = fields.Text("Reason for Leaving")
	total_years_of_experience = fields.Float("Total Years of Experience")
	relevant_years_of_experience = fields.Float("Relevant Years of Experience")
	relevant_yrs_of_exp_till_date = fields.Float("Relevant Years of Experience Till Date",compute="get_relavant_yrs_till_date", store=True)
	total_yrs_of_exp_till_date = fields.Float("Total Years of Experience Till Date",compute="get_total_yrs_till_date", store=True)



	#experienced documents
	previous_company_salary_slip = fields.Binary("Previous Company Last Month Salary Slip")
	previous_company_salary_slip2 = fields.Binary("Previous Company 2nd Last Month Salary Slip")
	previous_company_salary_slip3 = fields.Binary("Previous Company 3rd Last Month Salary Slip")
	last_company_releiving_letter =fields.Binary("Last Company releiving letter")
	last_company_experience_letter =fields.Binary("Last Company experience letter")
	last_company_offer_letter =fields.Binary("Last Company offer letter")


	#present and permanent address

	street_present = fields.Char(compute='getaddress',store=True)
	street2_present = fields.Char(compute='getaddress',store=True)
	zip_present = fields.Char(compute='getaddress',store=True, change_default=True)
	city_present = fields.Char(compute='getaddress',store=True)
	state_id_present = fields.Many2one("res.country.state",compute='getaddress',store=True,  ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	country_id_present = fields.Many2one('res.country', compute='getaddress',store=True,  ondelete='restrict')


	street_permanent = fields.Char(compute='getaddress',store=True)
	street2_permanent = fields.Char(compute='getaddress',store=True)
	zip_permanent = fields.Char(compute='getaddress',store=True, change_default=True)
	city_permanent = fields.Char(compute='getaddress',store=True)
	state_id_permanent = fields.Many2one("res.country.state",compute='getaddress',store=True, ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	country_id_permanent = fields.Many2one('res.country',compute='getaddress',store=True, ondelete='restrict')

	#off board 
	offboarding_type = fields.Selection([('exit_from_company', 'Exit From Company'), ('offboard_from_current_project', 'Offboard From Current Project')], string="Select Type")
	resigned_date = fields.Date()
	get_last_working_day = fields.Selection([('system', 'System'),('custom', 'Custom')], string="Get Last Working Day")
	notice_period = fields.Date(string="Notice Period(System Generate 2 months)",compute='get_notice_period')
	reason_for_resigning = fields.Many2one('hr.resign.reason')
	informed_client = fields.Selection([('yes','Yes'),('no','No')])
	notice_period_adjustable = fields.Char()

	#offboard_from project
	offboard_date_from_current_project = fields.Date()
	reasons_for_offboarding = fields.Many2one('hr.offboarding.reason')
	off_board_type = fields.Selection([('bench', 'Bench')], string="Off Board Type")

	project_id = fields.Many2one('project.project', 'Project Name')



	#off boarding details
	off_board = fields.Boolean()
	registration_number = fields.Char("	Registration Number of the Employee",copy=False, default=lambda self: _('New'))

	#probation and confirmation fields
	confirmation_types = fields.Selection([('probation', 'Probation'),('pip', 'PIP'),('confirmed', 'Confirmed')], string="Confirmation Type")
	pip_duration = fields.Selection([('1_month', '1 Month'),('2_month', '2 Month'),('3_month', '3 Month')], string="PIP Duration")
	confirmation_date = fields.Date(string='Confirmation Date',compute="get_confirmation_date", inverse="edit_date",store=True)

	confirmation_ref = fields.Char('Confirmation Reference', store=True,tracking=True)
	pip_ref = fields.Char('PIP Reference', store=True,tracking=True)
	relieving_letter_ref = fields.Char('Relieving Letter Reference', store=True,tracking=True)

	# @api.constrains('total_years_of_experience')
	# def _check_total_years_of_experience(self):
	# 	for record in self:
	# 		match = re.match(r'/^[0-9]*(\.[0-9]{0,2})?$/', str(record.total_years_of_experience))
	# 		if not match:
	# 			raise UserError(_('Not vallid years of experience'))

	@api.constrains('identification_id')
	def _check_aadharcard_number(self):
		for record in self:
			match = re.match(r'^[0-9]{12}$', record.identification_id)
			if not match:
				raise UserError(_('This is Not Valid Aadhar Number'))

	@api.constrains('pan_no')
	def _check_pan_num(self):
		for record in self:
			match = re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', record.pan_no)
			if not match:
				raise UserError(_('This is Not Valid PAN Number'))

	# @api.depends('confirmation_types')
	def update_sequence(self):
		for rec in self:
			if rec.confirmation_types == 'confirmed':
				rec.confirmation_ref = self.env['ir.sequence'].next_by_code('hr.employee.confirmation')
			elif rec.confirmation_types == 'pip':
				rec.pip_ref = self.env['ir.sequence'].next_by_code('hr.employee.pip')
			else:
				rec.confirmation_ref = False
				rec.pip_ref = False
	# @api.model
	def write(self, vals):
		res = super(HrEmployee, self).write(vals)
		if vals.get('confirmation_types'):
			self.update_sequence()
		if vals.get('offboarding_type'):
			self.get_relieving_letter_ref()
		return res

	# @api.depends('offboarding_type')
	def get_relieving_letter_ref(self):
		for rec in self:
			if rec.offboarding_type == 'exit_from_company':
				rec.relieving_letter_ref = self.env['ir.sequence'].next_by_code('hr.employee.relieving')
			else:
				rec.relieving_letter_ref = False





	@api.depends('date_of_joining','confirmation_types')
	def get_confirmation_date(self):
		for rec in self:
			if rec.date_of_joining and rec.confirmation_types == 'confirmed':
				rec.confirmation_date = rec.date_of_joining + relativedelta.relativedelta(months=3)
			else:
				rec.confirmation_date = False

	@api.depends('date_of_joining','confirmation_types')
	def edit_date(self):
		for rec in self:
			if rec.date_of_joining and rec.confirmation_types == 'confirmed':
				continue

	@api.model
	def create(self, vals):
		if 'registration_number' not in vals or vals['registration_number'] == _('New'):		
			if self.env.company.id == 1:
				vals['registration_number'] = self.env['ir.sequence'].next_by_code('hr.employee.india')
			else:
				vals['registration_number'] = self.env['ir.sequence'].next_by_code('hr.employee.singapore')
		result = super(HrEmployee, self).create(vals)
		return result


	@api.depends('date_of_joining','relevant_years_of_experience')
	def get_relavant_yrs_till_date(self):
		# self.ensure_one()
		for rec in self:
			rec.ensure_one()
			if rec.date_of_joining:

				start_date = rec.date_of_joining
				today = date.today() 

				diff = relativedelta.relativedelta(today, start_date)

				years = diff.years
				months = diff.months
				days = diff.days
				
				total_years_string = str(years) +"."+str("{:02d}".format(months))
				total_years_exp = round((rec.relevant_years_of_experience + float(total_years_string)),2)
				exp_split = str(total_years_exp).split('.')
				if int(exp_split[1])>=12:
					exp_split[0] = int(exp_split[0]) + 1 
					exp_split[1] = int(exp_split[1]) - 12
					total_years_exp = str(exp_split[0]) +"."+str("{:02d}".format(exp_split[1]))
				
				rec.relevant_yrs_of_exp_till_date = total_years_exp
			else:
				rec.relevant_yrs_of_exp_till_date = rec.relevant_years_of_experience

	@api.depends('date_of_joining','total_years_of_experience')
	def get_total_yrs_till_date(self):
		for rec in self:
			rec.ensure_one()
			if rec.date_of_joining and rec.total_years_of_experience !=None:
				start_date = rec.date_of_joining
				today = date.today() 

				diff = relativedelta.relativedelta(today, start_date)

				years = diff.years
				months = diff.months
				days = diff.days
				
				total_years_string = str(years) +"."+str("{:02d}".format(months))
				total_years_exp = round((rec.total_years_of_experience + float(total_years_string)),2)
				exp_split = str(total_years_exp).split('.')
				if int(exp_split[1])>=12:
					exp_split[0] = int(exp_split[0]) + 1 
					exp_split[1] = int(exp_split[1]) - 12
					total_years_exp = str(exp_split[0]) +"."+str("{:02d}".format(exp_split[1]))
				
				rec.total_yrs_of_exp_till_date = total_years_exp
			else:
				rec.total_yrs_of_exp_till_date = rec.total_years_of_experience




	@api.depends('get_last_working_day','resigned_date','notice_period_adjustable')
	def get_notice_period(self):
		for rec in self:
			if rec.get_last_working_day == 'system' and rec.resigned_date:
				start_date = rec.resigned_date
				# today = date.today() 
				two_months = start_date + relativedelta.relativedelta(months=2)
				rec.notice_period = two_months
			elif rec.get_last_working_day == 'custom' and rec.notice_period_adjustable:
				start_date = rec.resigned_date
				np_date= start_date + relativedelta.relativedelta(days=int(rec.notice_period_adjustable))
				rec.notice_period = np_date
			else:
				rec.notice_period = rec.notice_period

	# @api.depends('get_last_working_day','resigned_date','notice_period_adjustable')
	# def get_custom_np(self):
	# 	for rec in self:
	# 		if rec.get_last_working_day == 'custom' and rec.notice_period_adjustable:
	# 			start_date = rec.resigned_date
	# 			np_date= start_date + relativedelta.relativedelta(days=int(rec.notice_period_adjustable))
	# 			rec.notice_period = np_date
	# 		else:
	# 			rec.notice_period = rec.notice_period
	@api.model
	def send_birthday_wish(self):
		today_date = datetime.today().date()
		for employee in self.env['hr.employee'].search([]):
			if employee.birthday:
				if today_date.day == employee.birthday.day and today_date.month == employee.birthday.month:
					template_id = self.env.ref('instellars_custom_fields.email_birthday_wishes_employee_template')
					template_id.send_mail(employee.id, force_send=True)



	@api.depends('address_home_id')
	def getaddress(self):
		for address in self:
			address.street_present = address.address_home_id.street_present
			address.street2_present = address.address_home_id.street2_present
			address.zip_present = address.address_home_id.zip_present
			address.city_present = address.address_home_id.city_present
			address.state_id_present = address.address_home_id.state_id_present
			address.country_id_present = address.address_home_id.country_id_present
			address.street_permanent = address.address_home_id.street_permanent
			address.street2_permanent = address.address_home_id.street2_permanent
			address.zip_permanent = address.address_home_id.zip_permanent
			address.city_permanent = address.address_home_id.city_permanent
			address.state_id_permanent = address.address_home_id.state_id_permanent
			address.country_id_permanent = address.address_home_id.country_id_permanent

	def activate_offboard(self):
		if self.off_board:
			self.write({'off_board': False})
		else:
			self.write({'off_board': True})


	def send_confirmation(self):
		template = self.env.ref('instellars_custom_fields.conifrmation_letter_template', False)
		compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
		ctx = dict(
		    default_model="hr.employee",
		    default_res_id=self.id,
		    default_use_template=bool(template),
		    default_template_id=template.id,
		    default_composition_mode='comment',
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

	def send_pip(self):
		template = self.env.ref('instellars_custom_fields.pip_letter_template', False)
		compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
		ctx = dict(
		    default_model="hr.employee",
		    default_res_id=self.id,
		    default_use_template=bool(template),
		    default_template_id=template.id,
		    default_composition_mode='comment',
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

	def send_relieving(self):
		template = self.env.ref('instellars_custom_fields.relieving_letter_template', False)
		compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
		ctx = dict(
		    default_model="hr.employee",
		    default_res_id=self.id,
		    default_use_template=bool(template),
		    default_template_id=template.id,
		    default_composition_mode='comment',
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


	sign_request_count_probationary = fields.Integer(compute='probationary_review_sign_counts', store=True)

	def probationary_review_sign_counts(self):
		for rec in self:
			sign_from_role = self.env['sign.request.item'].search([
				('partner_id', '=', rec.user_id.partner_id.id),
				('sign_request_id.reference', 'ilike', 'Probationary'),
				('role_id', '=', self.env.ref('sign.sign_item_role_employee').id)]).mapped('sign_request_id')

			rec.sign_request_count_probationary = len(sign_from_role)

	def probationary_sign_request_open(self):
	    self.ensure_one()
	    
	    sign_from_role = self.env['sign.request.item'].search([
	        ('partner_id', '=', self.user_id.partner_id.id),
	        ('sign_request_id.reference', 'ilike', 'Probationary'),
	        ('role_id', '=', self.env.ref('sign.sign_item_role_employee').id)]).mapped('sign_request_id')
	    sign_request_ids = sign_from_role
	    if len(sign_request_ids.ids) == 1:
	        return sign_request_ids.go_to_document()

	    if self.env.user.has_group('sign.group_sign_user'):
	        view_id = self.env.ref("sign.sign_request_view_kanban").id
	    else:
	        view_id = self.env.ref("hr_contract_sign.sign_request_employee_view_kanban").id

	    return {
	        'type': 'ir.actions.act_window',
	        'name': 'Probationary Review Signature Requests',
	        'view_mode': 'kanban',
	        'res_model': 'sign.request',
	        'view_id': view_id,
	        'domain': [('id', 'in', sign_request_ids.ids)]
	    }


	@api.depends('user_id')
	def compute_tasks_count(self):
	    usr_id = 0

	    ir_model_data = self.env['ir.model.data']
	    search_view_id = ir_model_data.get_object_reference('project', 'view_task_search_form')[1]
	    for each in self:
	        if each.user_id:

	            project_task_ids = self.env['project.task'].search([('user_id', '=', each.user_id.id)])
	            length_count = len(project_task_ids)
	            each.task_count = length_count
	            usr_id = each.user_id.id
	        else:
	            each.task_count = 0
	            pass
	    return{
	        'name':'Employee Task',
	        'res_model':'project.task',
	        'type':'ir.actions.act_window',
	        'view_type':'form',
	        'view_mode':'list,form,kanban,calendar,pivot,graph',
	        'context':{'group_by':'stage_id'},
	        'domain': [('user_id', '=', usr_id)],
	        'search_view_id':search_view_id,
	     }

	task_count = fields.Integer(compute=compute_tasks_count,string='Task Count',readonly=True)



class Bank(models.Model):
    _inherit = 'res.bank'

    bank_branch = fields.Char('Branch')
    bank_ifsc_code = fields.Char('Bank IFSC Code')


# class ResumeLine(models.Model):
#     _inherit = 'hr.resume.line'






