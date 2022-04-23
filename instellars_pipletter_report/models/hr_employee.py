from odoo import fields, models, api,_
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
from num2words import num2words 


class HrApplicantfun(models.Model):
	_inherit = 'hr.employee'

	# def find_values(self):
	# 	for l in self:
	# 		if l.registration_number:
	# 			raise UserError(_('Raise eoorrrrrrrrrrrrrrr'))
	# 	return True

	def _get_report_lettername(self):
		self.ensure_one()

		return 'Performance Improvement Program Letter %s' % (self.name)

	def get_todaydate(self):
		today= datetime.today()
		dt = today.strftime("%B %d, %Y")
		return dt

	def ename_split(self, name):
		names=str(name)
		names= name.split(" ")
		return names[0]

	

