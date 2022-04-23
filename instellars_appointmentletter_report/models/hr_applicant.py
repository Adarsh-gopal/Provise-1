from odoo import fields, models, api,_
from datetime import datetime, timedelta, date
from num2words import num2words 


class HrApplicant(models.Model):
	_inherit = 'hr.applicant'

	def _get_report_base_file_name(self):
		self.ensure_one()
		return 'Appointment Letter %s - %s' % (self.partner_name, self.profile_id)

	def get_date_app(self):
		today= datetime.today()
		dt = today
		return dt

	def amount_in_words(self, amount):
		# return 'Rupees ' + num2words(amount,lang='en_IN').title()
		return num2words(amount,lang='en_IN').title() 

	def get_emp_details(self):
		emp=self.emp_id
		if emp:
			return emp.registration_number
		else:
			return 'Not an employee'

	def get_emp_details_fortitle(self):
		emp=self.emp_id
		if emp:
			return emp.title.name
		else: 
			return 'Not an employee'
			# eid=self.env['hr.payslip'].

	def ename_split(self, name):
		names=str(name)
		names= name.split(" ")
		return names[0]


class HrEmployee(models.Model):
	_inherit = 'hr.employee'


	last_sal= fields.Float(compute="_get_last_sal", store=True)

	def _get_last_sal(self):
		for rec in self:
			payslip_ids = []
			for ps in rec.slip_ids:
				payslip_ids.append(ps.id)
			if payslip_ids:
				payslip_id = max(payslip_ids)
				pid = self.env['hr.payslip'].browse(payslip_id)
				for line in pid.line_ids:
					if line.code == 'NET':
						rec.last_sal = line.total

			# print(payslip_id,'*******************************************')


class HrPublicEmployee(models.Model):
	_inherit = 'hr.employee.public'

	last_sal= fields.Float(readonly=True)


	
			