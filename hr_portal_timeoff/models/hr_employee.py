# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, time

from odoo import api, fields, models
from odoo.tools import float_round


class Employee(models.Model):
    _inherit = 'hr.employee'

    def _get_timeoff_portal_manager_id_domain(self):
        group = self.env.ref('hr_portal_timeoff.group_hr_timeoff_portal_approver', raise_if_not_found=False)
        return [('groups_id', 'in', [group.id])] if group else []

    timeoff_portal_manager_id = fields.Many2one(
        'res.users', string='Time Off Portal',
        domain=_get_timeoff_portal_manager_id_domain,
        help="User responsible of Timeoff validation. Should be Timeoff Manager.")

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    timeoff_portal_manager_id = fields.Many2one('res.users', string='Time Off Portal',
        help="User responsible of Timeoff validation. Should be Timeoff Manager.")