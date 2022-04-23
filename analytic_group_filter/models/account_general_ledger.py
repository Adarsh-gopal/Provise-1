# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.tools.misc import format_date
from odoo.addons.web.controllers.main import clean_action


class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = 'account.general.ledger'

    @api.model
    def _get_options_analytic_domain(self, options):
        domain = []
        if options.get('analytic_accounts'):
            analytic_account_ids = [int(acc) for acc in options['analytic_accounts']]
            domain.append(('analytic_account_id', 'in', analytic_account_ids))
        if options.get('analytic_tags'):
            analytic_tag_ids = [int(tag) for tag in options['analytic_tags']]
            domain.append(('analytic_tag_ids', 'in', analytic_tag_ids))
        if options.get('analytic_groups'):
            analytic_groups = [int(ag) for ag in options['analytic_groups']]
            domain.append(('analytic_account_id.group_id', 'in', analytic_groups))
        return domain
