from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Partner(models.Model):
	_inherit = 'res.partner'
	_description = 'respartner custom fields'

	vendor_code = fields.Char()


	street_present = fields.Char()
	street2_present = fields.Char()
	zip_present = fields.Char(change_default=True)
	city_present = fields.Char()
	state_id_present = fields.Many2one("res.country.state",  ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	country_id_present = fields.Many2one('res.country',  ondelete='restrict')


	street_permanent = fields.Char()
	street2_permanent = fields.Char()
	zip_permanent = fields.Char(change_default=True)
	city_permanent = fields.Char()
	state_id_permanent = fields.Many2one("res.country.state",  ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	country_id_permanent = fields.Many2one('res.country',  ondelete='restrict')