from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

class Demand2OpportunityPartner(models.TransientModel):

    _name = 'demands.demand2opportunity.partner'
    _description = 'Convert Demand to Opportunity'



    @api.model
    def default_get(self, fields):
        result = super(Demand2OpportunityPartner, self).default_get(fields)
        if self._context.get('active_id'):

            partner_id = result.get('partner_id')
            lead = self.env['demands'].browse(self._context['active_id'])

            if lead.partner_id:
                result['partner_id'] = lead.partner_id.id
            if lead.user_id:
                result['user_id'] = lead.user_id.id
        return result



    name = fields.Selection([
        ('convert', 'Convert to opportunity'),  
    ], 'Conversion Action', required=True, default='convert')
    user_id = fields.Many2one('res.users', index=True)
    partner_id = fields.Many2one('res.partner', 'Customer')



    def _convert_opportunity(self, vals):
        self.ensure_one()

        res = False

        demands = self.env['demands'].browse(vals.get('demand_ids'))
        for demand in demands:
            self_def_user = self.with_context(default_user_id=self.user_id.id)

            partner_id = vals.get('partner_id')
            res = demand.convert_opportunity(partner_id, [])

        return res

    def action_apply(self):
        self.ensure_one()
        values={}
        if self.partner_id:
            values['partner_id'] = self.partner_id.id

        if self.name == 'convert':
            demand = self.env['demands'].browse(self._context.get('active_ids', []))
            values.update({'demand_ids': demand.ids, 'user_ids': [self.user_id.id]})
            self._convert_opportunity(values)

        return demand[0].redirect_demand_opportunity_view()
