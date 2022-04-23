from odoo import fields, models, api,_
from datetime import datetime, timedelta, date
from num2words import num2words 


class HrApplicantfun(models.Model):
	_inherit = 'hr.employee'

	def _get_report_name(self):
		self.ensure_one()
		return 'Relieving Letter %s' % (self.name)

	def get_current_date(self):
		today= datetime.today()
		dt = today.strftime("%B %d, %Y")
		return dt

	def name_split(self, name):
		names=str(name)
		names= name.split(" ")
		return names[0]

	

