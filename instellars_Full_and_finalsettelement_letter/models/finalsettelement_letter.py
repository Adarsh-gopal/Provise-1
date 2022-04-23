from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from num2words import num2words 

class hrpayslip(models.Model):
	_inherit="hr.payslip"

	def get_date(self):
		today= datetime.today()
		dt = today.strftime("%d-%B-%Y")
		return dt

class hrpayslip(models.Model):
	_inherit="hr.payslip.line"

	def amount_words(self, amount):
		return num2words(amount,lang='en_IN').title() + ' Only '
		



