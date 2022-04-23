from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo import api, fields, models, _
from num2words import num2words
from calendar import monthrange 

class hrpayslip(models.Model):
	_inherit="hr.payslip"

	def get_currmonth(self):
		currmonth = self.name('%s' % (format_date(self.env, datefrom, date_format="MMMM y")))
		print(currmonth)

		return currmonth

	# def get_date_app(self):
	# 	today= datetime.today()
	# 	dt = today
	# 	return dt..strftime('%d-%B-%Y')

	def days_in_month(self,fromdate):
		month=fromdate.month
		year=fromdate.year
		daysinmonth=monthrange(year,month)
		return daysinmonth[1]

	def curr_month(self,fromdate):
		# month=fromdate.month
		# year=fromdate.year
		# daysinmonth=monthrange(year,month)
		return fromdate.strftime('%B')

	# def amount_words(self,amount):
	# 	s='(Rupees' + " " + num2words(amount,lang='en_IN').title() + ' Only)'
	# 	s = s.replace(',', '')
	# 	# print(s)
	# 	return s


class hrpayslipforactual(models.Model):
	_inherit="hr.payslip.inherit"

	def amount_words(self,amount):
		s='(Rupees' + " " + num2words(amount,lang='en_IN').title() + ' Only)'
		s = s.replace(',', '')
		# print(s)
		return s