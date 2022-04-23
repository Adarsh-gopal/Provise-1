from odoo import fields, models, api,_
from datetime import datetime, timedelta, date
from num2words import num2words 


class HrAppraisalForApp(models.Model):
	_inherit = 'hr.appraisal'

	def _get_report_base_filename(self):
		self.ensure_one()
		return 'Apprisal Letter %s' % (self.employee_id)

	def get_date(self):
		today= datetime.today()
		dt = today.strftime("%B %d, %Y")
		return dt

	def amount_in_words(self, amount):
		# return 'Rupees ' + num2words(amount,lang='en_IN').title()
		return num2words(amount,lang='en_IN').title() 

	def ename_split_fun(self, name):
		names=str(name)
		names= name.split(" ")
		return names[0]

# class HrEmployee(models.Model):
# 	_inherit = 'hr.employee'


# 	last_sal= fields.Float(compute="_get_last_sal", store=True)

# 	def _get_last_sal(self):
# 		for rec in self:
# 			payslip_ids = []
# 			for ps in rec.slip_ids:
# 				payslip_ids.append(ps.id)
# 			if payslip_ids:
# 				payslip_id = max(payslip_ids)
# 				pid = self.env['hr.payslip'].browse(payslip_id)
# 				for line in pid.line_ids:
# 					if line.code == 'NET':
# 						rec.last_sal = line.total

# 			# print(payslip_id,'*******************************************')


