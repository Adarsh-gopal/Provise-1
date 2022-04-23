# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.tools.misc import format_date
from odoo.addons.web.controllers.main import clean_action


class AnalyticReport(models.AbstractModel):
    _inherit = 'account.report'

    def _set_context(self, options):
        res = super(AnalyticReport, self)._set_context(options)
        if options.get('analytic_groups'):
            AA = self.env['account.analytic.account']
            groups = self.env['account.analytic.group'].browse([int(group) for group in options['analytic_groups']])
            if groups:
                analytic_account_ids = self.env['account.analytic.account'].search([('group_id', 'in', groups.ids)])
                if analytic_account_ids:
                    res['analytic_account_ids'] = res.get('analytic_account_ids', AA) + analytic_account_ids
        return res

    @api.model
    def _init_filter_analytic(self, options, previous_options=None):
        if not self.filter_analytic:
            return

        options['analytic'] = self.filter_analytic

        if self.user_has_groups('analytic.group_analytic_accounting'):
            options['analytic_accounts'] = previous_options and previous_options.get('analytic_accounts') or []
            options['analytic_groups'] = previous_options and previous_options.get('analytic_groups') or []
            analytic_account_ids = [int(acc) for acc in options['analytic_accounts']]
            analytic_groups_ids = [int(ag) for ag in options['analytic_groups']]
            selected_analytic_accounts = analytic_account_ids \
                                         and self.env['account.analytic.account'].browse(analytic_account_ids) \
                                         or self.env['account.analytic.account']
            selected_analytic_groups = analytic_groups_ids \
                                         and self.env['account.analytic.group'].browse(analytic_groups_ids) \
                                         or self.env['account.analytic.group']                                         
            options['selected_analytic_account_names'] = selected_analytic_accounts.mapped('name')
            options['selected_analytic_groups'] = selected_analytic_groups.mapped('name')
        if self.user_has_groups('analytic.group_analytic_tags'):
            options['analytic_tags'] = previous_options and previous_options.get('analytic_tags') or []
            analytic_tag_ids = [int(tag) for tag in options['analytic_tags']]
            selected_analytic_tags = analytic_tag_ids \
                                     and self.env['account.analytic.tag'].browse(analytic_tag_ids) \
                                     or self.env['account.analytic.tag']
            options['selected_analytic_tag_names'] = selected_analytic_tags.mapped('name')

    def _with_correct_filters1(self):
        return self

    def get_report_informations(self, options):
        if options and options.get('analytic') and options.get('analytic_groups'):
            options['selected_analytic_groups'] = options['analytic_groups'] and [self.env['account.analytic.group'].browse(int(group)).name for group in options['analytic_groups']] or []
        return super(AnalyticReport, self._with_correct_filters1()).get_report_informations(options)
