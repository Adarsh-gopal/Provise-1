from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, date_utils
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil import relativedelta


class Applicant(models.Model):
	_inherit = "hr.applicant"

	#perosnal details
	skype_id = fields.Char("Skype Id")
	linkedin_url = fields.Char("Linkedin URL")

	#Education
	course = fields.Char("Course")
	course_id = fields.Many2many('educational.course',string='Courses')
	year_of_passing = fields.Selection([((str(num)), (str(num))) for num in range(1900, (datetime.now().year)+1)], 'Year of Passing')

	#Reffered By
	vendor_name =fields.Char()
	referral_channel = fields.Selection([('Referral-Internal', 'Referral - Internal'), ('Referral-External', 'Referral - External')], string="Referral Channel")
	source_name =fields.Char()#dummy field to get the vendor selected based on the following getname() method to filter vendor_name field

	@api.onchange('source_id')
	def getname(self):
		self.source_name = self.source_id.name 

	profile_id =  fields.Char(string="Profile ID", required=True,  copy=False, default='New')

	@api.model
	def create(self, vals):
		if vals.get('profile_id', 'New') == 'New':
			vals['profile_id'] = self.env['ir.sequence'].next_by_code('hr.applicant') or 'New'       

		result = super(Applicant, self).create(vals)       

		return result

	



    #prosessional related fields
	current_company_of_applicant = fields.Many2one('res.partner', 'Current Company')
	employment_start_date = fields.Date()
	total_years_of_experience = fields.Float(compute='get_total_years_exp',store=True)
	relevant_start_date = fields.Date()
	relevant_years_of_experience = fields.Float(compute='get_relavant_years_exp', store=True)
	current_salary = fields.Float('Current CTC')
	included_variable_pay = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Included Variable Pay")
	expected_ctc_type = fields.Selection([('fixed_hike', 'Fixed hike'), ('variable_hike', 'Variable hike')], string="Expected CTC Type")
	current_designation = fields.Char()
	no_of_project_worked = fields.Integer('No of Project Worked')
	reason_for_change = fields.Many2one('hr.change.reason')

    #resume related fields
	current_country = fields.Many2one('res.country')
	preferred_country = fields.Many2one('res.country')
	current_location = fields.Many2one('hr.location')
	preferred_location = fields.Many2one('hr.location')
	willing_to_relocate = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Willing To Relocate?")
	permanent_residency = fields.Many2one('res.country')
	resume_received = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Resume Received?")
	resume_received_date = fields.Date()
	notice_period_type = fields.Selection([('serving_np', 'Serving NP'), ('yet_to_serve_np', 'Yet to Serve NP')], string="Notice Period Type")
	notice_period = fields.Integer('Notice Period(Days)')
	date_of_last_working_day = fields.Date()
	expected_date_of_joining = fields.Date()
	resignation_acceptance = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('pending', 'Pending')], string="Resignation Acceptance?")
	certification_type = fields.Many2one('hr.skill.type')
	certification = fields.Many2many('hr.skill')
	resume_upload = fields.Binary()
	calculate_tot_yrs_exp = fields.Selection([('custom', 'Custom'), ('automatic', 'Automatic')], string="Calculate Total Experience")
	calculate_tot_relavant_yrs_exp = fields.Selection([('custom', 'Custom'), ('automatic', 'Automatic')], string="Calculate Total Relavant Experience")

	#only if cirtification type is PEGA
	pdn_number = fields.Char("PDN")
	appointment_letter_sequence = fields.Char('Appointment Ref', compute="get_appointment_sequence",store=True, tracking=True)

	@api.depends('emp_id')
	def get_appointment_sequence(self):
		for rec in self:
			if rec.emp_id:
				rec.appointment_letter_sequence = self.env['ir.sequence'].next_by_code('hr.employee.appointment')
			else:
				rec.appointment_letter_sequence = False



	@api.depends('calculate_tot_yrs_exp','employment_start_date')
	def get_total_years_exp(self):
		for rec in self:
			if rec.calculate_tot_yrs_exp == 'automatic':
				start_date = rec.employment_start_date
				today = date.today() 

				diff = relativedelta.relativedelta(today, start_date)

				years = diff.years
				months = diff.months
				days = diff.days
				total_years_string = str(years) +"."+str("{:02d}".format(months))
				total_years_exp = float(total_years_string)
				rec.total_years_of_experience = total_years_exp
			else:
				rec.total_years_of_experience = rec.total_years_of_experience


	@api.depends('calculate_tot_relavant_yrs_exp','relevant_start_date')		
	def get_relavant_years_exp(self):
		for rec in self:
			if rec.calculate_tot_relavant_yrs_exp == 'automatic':
				start_date = rec.relevant_start_date
				today = date.today() 

				diff = relativedelta.relativedelta(today, start_date)

				years = diff.years
				months = diff.months
				days = diff.days
				total_relavant_yrs_string = str(years) +"."+str("{:02d}".format(months))
				total_relavant_yrs_exp = float(total_relavant_yrs_string)
				rec.relevant_years_of_experience = total_relavant_yrs_exp
			else:
				rec.relevant_years_of_experience =rec.relevant_years_of_experience










