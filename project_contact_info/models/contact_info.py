from odoo import api, fields, models

class Project(models.Model):
    _inherit = 'project.project'

    contact_info_company_line_ids = fields.One2many('project.contact.info.company.line', 'project_id', string="Company Contact Line ids ")
    contact_info_client_line_ids = fields.One2many('project.contact.info.client.line', 'project_id', string="Client Contact Line ids")

#company side contacts
class ProjectContactInfoCompanyLine(models.Model):
	_name = 'project.contact.info.company.line'
	_description = "contact info for Project"
	_order = "line_type_id"

	project_id = fields.Many2one('project.project', required=True, ondelete='cascade')
	name_main = fields.Many2one('res.partner')
	phone_main = fields.Char()
	email_main = fields.Char()
	name_cc = fields.Many2one('res.partner')
	phone_cc = fields.Char()
	email_cc = fields.Char()
	description = fields.Text(string="Description")
	line_type_id = fields.Many2one('project.contact.info.line.type', string="Type")


	# Used to apply specific template on a line
	display_type = fields.Selection([('classic', 'Classic')], string="Display Type", default='classic')

	@api.onchange('name_main')
	def getmainname(self):
		self.phone_main = self.name_main.phone
		self.email_main = self.name_main.email

	@api.onchange('name_cc')
	def getccname(self):
		self.phone_cc = self.name_cc.phone
		self.email_cc = self.name_cc.email


#client side contacts
class ProjectContactInfoClientLine(models.Model):
	_name = 'project.contact.info.client.line'
	_description = "contact info for Project"
	_order = "line_type_id"

	project_id = fields.Many2one('project.project', required=True, ondelete='cascade')
	name_main = fields.Many2one('res.partner')
	job_position = fields.Char()
	phone_main = fields.Char()
	email_main = fields.Char()
	name_cc = fields.Many2one('res.partner')
	phone_cc = fields.Char()
	email_cc = fields.Char()
	description = fields.Text(string="Description")
	line_type_id = fields.Many2one('project.contact.info.line.type', string="Type")


	# Used to apply specific template on a line
	display_type = fields.Selection([('classic', 'Classic')], string="Display Type", default='classic')

	@api.onchange('name_main')
	def getmainname(self):
		self.phone_main = self.name_main.phone
		self.email_main = self.name_main.email

	@api.onchange('name_cc')
	def getccname(self):
		self.phone_cc = self.name_cc.phone
		self.email_cc = self.name_cc.email




class ProjectContactInfoLineType(models.Model):
    _name = 'project.contact.info.line.type'
    _description = "Type of a contact"
    _order = "sequence"

    name = fields.Char(required=True)
    groups = fields.Selection([('client_group', 'Client Group'), ('company_group', 'Company Group')], string="Contact Groups",default='company_group', required=True)
    sequence = fields.Integer('Sequence', default=10)
