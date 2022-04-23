from odoo import fields, models, api,_
from datetime import datetime, timedelta, date
from num2words import num2words
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
import pdb


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	def _get_report_base_filename(self):
		self.ensure_one()
		return 'Confirmation Letter %s' % (self.name)

	def get_date(self):
		today= self.confirmation_date
		dt = today.strftime("%B %d, %Y")
		return dt

	def get_today_date(self):
		today= datetime.today()
		dt = today.strftime("%B %d, %Y")
		return dt

	def get_company_name(self):
		for l in self:
			x=0
			name = l.company_id.name
			x = name.split(' ')
			y = x[0]
		return y

	def get_name(self):
		for l in self:
			x=0
			name = l.name
			x = name.split(' ')
			y = x[0]
		return y

	def amount_words(self, amount):
		return 'Rupees ' + num2words(amount,lang='en_IN').title() 




