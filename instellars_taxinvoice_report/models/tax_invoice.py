from odoo import api, fields, models,_
from odoo.exceptions import UserError
import pdb
import datetime
from datetime import timedelta
from num2words import num2words 

class taxinvoice(models.Model):
	_inherit="account.move.line"

	def calculategst(self,tax):
		cgst_amt =0.0
		sgst_amt =0.0
		tax_amount=0.0
		for tax in self.tax_ids:
			tax_amount = self.price_subtotal *(self.tax_ids.amount/2)/100
			print("Tax",tax_amount)

		return tax_amount

 
class taxinvoice1(models.Model):
	_inherit="account.move"

	def tax_split(self,tax):
		# taxes=str(tax)
		taxes= tax.split(" ")
		return taxes[0] + " " +'@'+ " " + taxes[1]


	def amount_words(self, amount):
		if self.currency_id.name == 'SGD':
			return ' Singapore Dollar ' + " "  + num2words(amount,lang='en_IN').title() + ' Only '

		if self.currency_id.name != 'SGD':
			return self.currency_id.name + " "  + num2words(amount,lang='en_IN').title() + ' Only '

	def duedate(self):
		# today=date.today()
		# sale_rec_ids=self.env['sale.order'].search([('name','=',origin)])
		# rec_date=sale_rec_ids.date_order
		# rec_date - timedelta(days=30).date()
		current_date=self.invoice_date

		# pdb.set_trace()
		no_of_days =0
		if self.invoice_payment_term_id.id:
			for line in self.invoice_payment_term_id.line_ids:
				no_of_days=line.days

		pay_date=current_date + timedelta(days=no_of_days)
		du_date=pay_date.strftime('%d-%b-%Y')
		return du_date

	# def duedate(self,origin):
	# 	# today=date.today()
	# 	sale_rec_ids=self.env['sale.order'].search([('name','=',origin)])
	# 	rec_date=sale_rec_ids.date_order
	# 	# rec_date - timedelta(days=30).date()

	# 	# pdb.set_trace()
	# 	no_of_days =0
	# 	if self.invoice_payment_term_id.id:
	# 		for line in self.invoice_payment_term_id.line_ids:
	# 			no_of_days=line.days

	# 	current_date=rec_date + timedelta(days=no_of_days)
	# 	du_date=current_date.strftime('%d-%b-%Y')
	# 	return du_date

	def get_orderdate_forinvoice(self,source):
		sale_id=self.env['sale.order'].search([('name','=',source)])

		return sale_id.date_order

	def get_orderdate_for_invoice(self,source):
		sale_id=self.env['sale.order'].search([('name','=',source)])

		return sale_id.vendor_code

	def get_orderdate_for_pt(self,source):
		sale_id=self.env['sale.order'].search([('name','=',source)])

		return sale_id.payment_term_id.name

	def get_purchaseno_forinvoice(self,source):
		sale_id=self.env['sale.order'].search([('name','=',source)])

		return sale_id.purchase_order_number

	def get_purchasedate_forinvoice(self,source):
		sale_id=self.env['sale.order'].search([('name','=',source)])

		return sale_id.purchase_order_date

	def date_split(self,serviceperiod):
		remove= serviceperiod.replace("-"," ")
		return remove

		
 







		
		

	





	


