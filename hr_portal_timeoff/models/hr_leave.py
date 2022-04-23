import logging
import math

from collections import namedtuple

from datetime import datetime, date, timedelta, time
from pytz import timezone, UTC

from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _

DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    z_name = fields.Char(related='name', string="Dup Name",store=True)


    # @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
    #               'request_date_from', 'request_date_to',
    #               'employee_id')
    def onchange_portal_request_params(self,request_date_from_period,request_hour_from,request_hour_to,request_date_from,request_date_to,employee_id,request_unit_half,request_unit_hours):
        # print('*************',self.env.user.lang)
        request_date_from = datetime.strptime(request_date_from, '%Y-%m-%d')
        request_date_to = datetime.strptime(request_date_to,  '%Y-%m-%d')
        request_unit_custom = False
        if not request_date_from:
            date_from = False
            return

        if request_unit_half or request_unit_hours:
            request_date_to = request_date_from

        if not request_date_to:
            date_to = False
            return
        employee = self.env['hr.employee'].sudo().browse(employee_id)
        resource_calendar_id = employee.resource_calendar_id or self.env.company.resource_calendar_id
        domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
        attendances = self.env['resource.calendar.attendance'].sudo().read_group(domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'week_type', 'dayofweek', 'day_period'], ['week_type', 'dayofweek', 'day_period'], lazy=False)

        # Must be sorted by dayofweek ASC and day_period DESC
        attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))

        default_value = DummyAttendance(0, 0, 0, 'morning', False)

        if resource_calendar_id.two_weeks_calendar:
            # find week type of start_date
            start_week_type = int(math.floor((request_date_from.toordinal() - 1) / 7) % 2)
            attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == start_week_type]
            attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != start_week_type]
            # First, add days of actual week coming after date_from
            attendance_filtred = [att for att in attendance_actual_week if int(att.dayofweek) >= request_date_from.weekday()]
            # Second, add days of the other type of week
            attendance_filtred += list(attendance_actual_next_week)
            # Third, add days of actual week (to consider days that we have remove first because they coming before date_from)
            attendance_filtred += list(attendance_actual_week)

            end_week_type = int(math.floor((request_date_to.toordinal() - 1) / 7) % 2)
            attendance_actual_week = [att for att in attendances if att.week_type is False or int(att.week_type) == end_week_type]
            attendance_actual_next_week = [att for att in attendances if att.week_type is False or int(att.week_type) != end_week_type]
            attendance_filtred_reversed = list(reversed([att for att in attendance_actual_week if int(att.dayofweek) <= request_date_to.weekday()]))
            attendance_filtred_reversed += list(reversed(attendance_actual_next_week))
            attendance_filtred_reversed += list(reversed(attendance_actual_week))

            # find first attendance coming after first_day
            attendance_from = attendance_filtred[0]
            # find last attendance coming before last_day
            attendance_to = attendance_filtred_reversed[0]
        else:
            # find first attendance coming after first_day
            attendance_from = next((att for att in attendances if int(att.dayofweek) >= request_date_from.weekday()), attendances[0] if attendances else default_value)
            # find last attendance coming before last_day
            attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= request_date_to.weekday()), attendances[-1] if attendances else default_value)

        compensated_request_date_from = request_date_from
        compensated_request_date_to = request_date_to

        if request_unit_half:
            if request_date_from_period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
        elif request_unit_hours:
            hour_from = float_to_time(float(request_hour_from))
            hour_to = float_to_time(float(request_hour_to))
        elif request_unit_custom:
            hour_from = date_from.time()
            hour_to = date_to.time()
            compensated_request_date_from = self._adjust_date_based_on_tz(request_date_from, hour_from)
            compensated_request_date_to = self._adjust_date_based_on_tz(request_date_to, hour_to)
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)

        tz = self.env.user.tz if self.env.user.tz and not request_unit_custom else 'UTC'  # custom -> already in UTC

        date_from = timezone(tz).localize(datetime.combine(compensated_request_date_from, hour_from)).astimezone(UTC).replace(tzinfo=None)
        date_to = timezone(tz).localize(datetime.combine(compensated_request_date_to, hour_to)).astimezone(UTC).replace(tzinfo=None)

        num_of_days = self.onchange_portal_dates(date_from, date_to, employee)

        res = {'date_from':date_from,'date_to':date_to, 'num_of_days':num_of_days}

        #for holiday calcluations
        delta = request_date_to - request_date_from
        date_dict = [] 

        for i in range(delta.days + 1):
            day = request_date_from + timedelta(days=i)
            date_dict.append(day.date())

        if resource_calendar_id:
            holiday_lst = resource_calendar_id.global_leave_ids.filtered(lambda l: l.date_to.date() in date_dict)

        if holiday_lst:
            holiday_dict = []
            for hl in holiday_lst:
                holiday_dict.append({'name':hl.name,'date':hl.date_to.strftime('%d-%m-%Y')})
            if holiday_dict:
                res['holiday_list'] = holiday_dict

        return res

        # self.update({'date_from': date_from, 'date_to': date_to})
        # self._onchange_leave_dates()


    def onchange_portal_dates(self,date_from,date_to,employee_id):
        if date_from and date_to:
            return  self._get_number_of_days(date_from, date_to, employee_id.id)['days']
        else:
            return 0


    def get_holiday_request_unit(self, status_id):
        if status_id:
            holiday_type = self.env['hr.leave.type'].browse(status_id)

            return holiday_type.request_unit




    # @api.model
    def write(self, values):
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_portal = self.env.user.sudo().has_group('base.group_portal')

        if not is_officer:
            if not is_portal:
                if any(hol.date_from.date() < fields.Date.today() for hol in self):
                    raise UserError(_('You must have manager rights to modify/validate a time off that already begun'))

        employee_id = values.get('employee_id', False)
        if not self.env.context.get('leave_fast_create'):
            if values.get('state'):
                self._check_approval_update(values['state'])
                if any(holiday.validation_type == 'both' for holiday in self):
                    if values.get('employee_id'):
                        employees = self.env['hr.employee'].browse(values.get('employee_id'))
                    else:
                        employees = self.mapped('employee_id')
                    self._check_double_validation_rules(employees, values['state'])
            if 'date_from' in values:
                values['request_date_from'] = values['date_from']
            if 'date_to' in values:
                values['request_date_to'] = values['date_to']
        result = super(models.Model, self).write(values)
        if not self.env.context.get('leave_fast_create'):
            for holiday in self:
                if employee_id:
                    holiday.add_follower(employee_id)
                    self._sync_employee_details()
                if 'number_of_days' not in values and ('date_from' in values or 'date_to' in values):
                    holiday._onchange_leave_dates()
        return result


    def _check_double_validation_rules(self, employees, state):
        if self.user_has_groups('hr_holidays.group_hr_holidays_manager'):
            return

        is_leave_user = self.user_has_groups('hr_holidays.group_hr_holidays_user') or self.user_has_groups('hr_portal_timeoff.group_hr_timeoff_portal_approver')
        if state == 'validate1':
            employees = employees.filtered(lambda employee: employee.leave_manager_id != self.env.user)
            if employees and not is_leave_user:
                raise AccessError(_('You cannot first approve a leave for %s, because you are not his leave manager' % (employees[0].name,)))
        elif state == 'validate' and not is_leave_user:
            # Is probably handled via ir.rule
            raise AccessError(_('You don\'t have the rights to apply second approval on a leave request'))



class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    def get_days(self, employee_id):
        # need to use `dict` constructor to create a dict per id
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)

        requests = self.env['hr.leave'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['draft','confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids)
        ])

        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids)
        ])

        for request in requests:
            status_dict = result[request.holiday_status_id.id]
            status_dict['virtual_remaining_leaves'] -= (request.number_of_hours_display
                                                    if request.leave_type_request_unit == 'hour'
                                                    else request.number_of_days)
            if request.state == 'validate':
                status_dict['leaves_taken'] += (request.number_of_hours_display
                                            if request.leave_type_request_unit == 'hour'
                                            else request.number_of_days)
                status_dict['remaining_leaves'] -= (request.number_of_hours_display
                                                if request.leave_type_request_unit == 'hour'
                                                else request.number_of_days)

        for allocation in allocations.sudo():
            status_dict = result[allocation.holiday_status_id.id]
            if allocation.state == 'validate':
                # note: add only validated allocation even for the virtual
                # count; otherwise pending then refused allocation allow
                # the employee to create more leaves than possible
                status_dict['virtual_remaining_leaves'] += (allocation.number_of_hours_display
                                                          if allocation.type_request_unit == 'hour'
                                                          else allocation.number_of_days)
                status_dict['max_leaves'] += (allocation.number_of_hours_display
                                            if allocation.type_request_unit == 'hour'
                                            else allocation.number_of_days)
                status_dict['remaining_leaves'] += (allocation.number_of_hours_display
                                                  if allocation.type_request_unit == 'hour'
                                                  else allocation.number_of_days)

        return result

