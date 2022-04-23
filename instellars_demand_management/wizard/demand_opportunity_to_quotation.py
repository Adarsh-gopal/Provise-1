# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DemandOpportunity2Quotation(models.TransientModel):

    _name = 'demand.quotation.partner'
    _description = 'Create new or use existing Customer on new Quotation'

    @api.model
    def default_get(self, fields):
        result = super(DemandOpportunity2Quotation, self).default_get(fields)
        partner_id = self._find_matching_partner()

        active_model = self._context.get('active_model')
        if active_model != 'demands':
            raise UserError(_('You can only apply this action from a demands.'))

        active_id = self._context.get('active_id')
        if 'demand_id' in fields and active_id:
            result['demand_id'] = active_id
        if 'partner_id' in fields:
            result['partner_id'] = partner_id
        return result

    action = fields.Selection([
        ('create', 'Create a new customer'),
        ('exist', 'Link to an existing customer'),
        ('nothing', 'Do not link to a customer')
    ], 'Related Customer', required=True)
    demand_id = fields.Many2one('demands', "Associated Lead", required=True)
    partner_id = fields.Many2one('res.partner', 'Customer')

    def action_apply(self):
        """ Convert lead to opportunity or merge lead and opportunity and open
            the freshly created opportunity view.
        """
        self.ensure_one()
        if self.action != 'nothing':
            self.demand_id.write({
                'partner_id': self.partner_id.id if self.action == 'exist' else self._create_partner()
            })
            self.demand_id._onchange_partner_id()
        return self.demand_id.action_new_quotation()

    def _create_partner(self):
        """ Create partner based on action.
            :return int: created res.partner id
        """
        self.ensure_one()
        result = self.demand_id.handle_partner_assignation(action='create')
        return result.get(self.demand_id.id)


    @api.model
    def _find_matching_partner(self):
        if self._context.get('active_model') != 'demands' or not self._context.get('active_id'):
            return False

        demand = self.env['demands'].browse(self._context.get('active_id'))

        # find the best matching partner for the active model
        Partner = self.env['res.partner']
        if demand.partner_id:  # a partner is set already
            return demand.partner_id.id

        if demand.email_from:  # search through the existing partners based on the demand's email
            partner = Partner.search([('email', '=', demand.email_from)], limit=1)
            return partner.id

        if demand.partner_name:  # search through the existing partners based on the demand's partner or contact name
            partner = Partner.search([('name', 'ilike', '%' + demand.partner_name + '%')], limit=1)
            return partner.id

        if demand.contact_name:
            partner = Partner.search([('name', 'ilike', '%' + demand.contact_name+'%')], limit=1)
            return partner.id

        if demand.name: # to be aligned with _create_demand_partner, search on demand's name as last possibility
            partner = Partner.search([('name', 'ilike', '%' + demand.name + '%')], limit=1)
            return partner.id

        return False

