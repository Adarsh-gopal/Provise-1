# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, time

from odoo import api, fields, models
from odoo.tools import float_round


class Employee(models.Model):
    _inherit = 'hr.employee'

    def _get_timesheet_portal_manager_id_domain(self):
        group = self.env.ref('portal_timesheet.group_hr_timesheet_portal_approver', raise_if_not_found=False)
        return [('groups_id', 'in', [group.id])] if group else []

    timesheet_portal_manager_id = fields.Many2one(
        'res.users', string='Timesheet Portal',
        domain=_get_timesheet_portal_manager_id_domain,
        help="User responsible of timesheet validation. Should be Timesheet Manager.")

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    timesheet_portal_manager_id = fields.Many2one('res.users', string='Timesheet Portal',
        help="User responsible of timesheet validation. Should be Timesheet Manager.")