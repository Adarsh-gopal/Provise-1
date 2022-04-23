from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo import api, fields, models, _
from num2words import num2words 

class hrpayslip(models.Model):
	_inherit="hr.payslip"

	final_settlement_information=fields.Boolean(string="Final Settlement?")

	def get_currmonth(self):
		currmonth = self.name('%s' % (format_date(self.env, datefrom, date_format="MMMM y")))
		print(currmonth)

		return currmonth

class hrpayslip(models.Model):
	_inherit="hr.payslip.line"

	def amount_words(self, amount):
		return 'Rupees' + " " + num2words(amount,lang='en_IN').title() + ' Only '

class HrEmployee(models.Model):
	_inherit="hr.employee"

	lastsalpaid_date = fields.Date('Last Salary Paid On', groups="hr.group_hr_user", compute="get_last_payslip_date", store=True)

	@api.depends('slip_ids')
	def get_last_payslip_date(self):
		for rec in self:
			if rec.slip_ids:
				payslip_ids = []
				for ps in rec.slip_ids:
					if ps.final_settlement_information == False:
						payslip_ids.append(ps.id)
				if payslip_ids:
					payslip_id = max(payslip_ids)
					pid = self.env['hr.payslip'].browse(payslip_id)
					rec.lastsalpaid_date=pid.date_from
				else:
					rec.lastsalpaid_date = None
			else:
				rec.lastsalpaid_date = None

				# for line in pid.line_ids:
				# 	if line.code == 'NET':
				# 		rec.lastsalpaid = line.total
						

