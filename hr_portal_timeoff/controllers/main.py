# -*- coding: utf-8 -*-
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from datetime import date
from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND
from werkzeug.wsgi import get_current_url
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class TimeoffCustomerPortal(CustomerPortal):

    def get_manager_status(self):
        manager = request.env['hr.employee'].sudo().search_count([('timeoff_portal_manager_id', '=' , request.env.user.id)])
        if manager > 0:
            return True
        else:
            return False


    def get_holiday_list(self):
        employee= request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        return employee.resource_calendar_id.global_leave_ids.filtered(lambda a: a.date_to.year == date.today().year)

    def _prepare_portal_layout_values(self):
        values = super(TimeoffCustomerPortal, self)._prepare_portal_layout_values()
        # domain = request.env['hr.leave']._timesheet_get_portal_domain()
        values['timeoff_count'] = request.env['hr.leave'].sudo().search_count([('employee_id.user_id', '=' , request.env.user.id)])
        values['team_timeoff_count'] = request.env['hr.leave'].sudo().search_count([('employee_id.timeoff_portal_manager_id', '=' , request.env.user.id)])
        values['holiday_status'] = request.env['hr.leave.type'].sudo().search([])
        values['allocations'] = request.env['hr.leave.allocation'].sudo().search([('employee_id.user_id', '=' , request.env.user.id)])
        values['tmoff_summary'] =request.env['hr.leave.type'].sudo().get_days_all_request()
        values['holiday_list'] =self.get_holiday_list()
        values['is_timeoff_manager'] = self.get_manager_status()
        values['original_link'] = get_current_url(request.httprequest.environ)
        return values

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timeoff(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='Time Off Type', **kw):
        Timeoff_sudo = request.env['hr.leave'].sudo()
        values = self._prepare_portal_layout_values()
        domain = [('employee_id.user_id', '=' , request.env.user.id)]

        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'Time Off Type': {'input': 'holiday_status_id', 'label': _('Time Off Type')},
        }

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("create_date", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('create_date', '>=', date_utils.start_of(today, "week")), ('create_date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('create_date', '>=', date_utils.start_of(today, 'month')), ('create_date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('create_date', '>=', date_utils.start_of(today, 'year')), ('create_date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('create_date', '>=', quarter_start), ('create_date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('create_date', '>=', date_utils.start_of(last_week, "week")), ('create_date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('create_date', '>=', date_utils.start_of(last_month, 'month')), ('create_date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('create_date', '>=', date_utils.start_of(last_year, 'year')), ('create_date', '<=', date_utils.end_of(last_year, 'year'))]},
        }
        # default sort by value
        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain = AND([domain, [('name', 'ilike', search)]])

        timeoff_count = Timeoff_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/leaves",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=timeoff_count,
            page=page,
            step=self._items_per_page
        )

        if groupby == 'Time Off Type':
            order = "holiday_status_id, %s" % order
        timeoffs = Timeoff_sudo.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'Time Off Type':
            grouped_leaves = [Timeoff_sudo.concat(*g) for k, g in groupbyelem(timeoffs, itemgetter('holiday_status_id'))]
        else:
            grouped_leaves = [timeoffs]

        values.update({
            'timeoffs': timeoffs,
            'grouped_leaves': grouped_leaves,
            'page_name': 'my_leaves',
            'default_url': '/my/leaves',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("hr_portal_timeoff.portal_my_leaves", values)


    def create_new_timeoff(self, form_data, **kw):
        holiday_status_id = request.env['hr.leave.type'].sudo().browse(form_data['holiday_status_id'])

        leave_days = holiday_status_id.get_days(form_data['employee_id'])[holiday_status_id.id]
        print(leave_days,'**********************************')
        if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
            raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                                    'Please also check the time off waiting for validation.'))
        if leave_days['remaining_leaves'] < form_data['number_of_days'] or leave_days['virtual_remaining_leaves'] < form_data['number_of_days']:
            raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                                    'Please also check the time off waiting for validation.'))


        if form_data:
            time_off = request.env['hr.leave'].sudo().create({
                'name': form_data['description'],
                'holiday_status_id': form_data['holiday_status_id'],
                'request_date_from': form_data['request_from_date'],
                'request_date_to': form_data['request_to_date'],
                'employee_id': form_data['employee_id'],
                'request_unit_half': form_data['half_day'],
                'request_unit_hours': form_data['request_unit_hours'],
                'request_unit_custom': False,
                'payslip_status': False,
                'request_hour_from': form_data['request_hours_from'],
                'request_hour_to': form_data['request_hours_to'],
                'number_of_days': form_data['number_of_days'],
                'date_from': form_data['date_from'],
                'date_to': form_data['date_to'],
                'state':'draft',
            })

            # task_timesheet = task.write({'timesheet_ids': [(0,0,prepare_timesheet_ids)] })

        return time_off

    @http.route(['/portal/timeoff/request/'], type='json', auth="user")
    def submit_timeoff_request(self, form_data, **kw):
        timeoff_data = self.create_new_timeoff(form_data, **kw)

        return {'timeoff_id': timeoff_data,'error': 0,}



    @http.route(['/my/leaves/<int:leave_id>'], type='http', auth="user", website=True)
    def portal_my_leave_edit(self, leave_id, access_token=None, **kw):
        if leave_id:
            leave = request.env['hr.leave'].sudo().browse(leave_id)
        # values = self._task_get_page_view_values(task_sudo, access_token, **kw)

        if leave:
            if leave.state not in ['draft','confirm']:
                return request.redirect('/my/leaves')

        values = {
            'page_name' : 'edit_leave',
            'leave':leave,
            'holiday_status':request.env['hr.leave.type'].sudo().search([]),
            'tmoff_summary' : request.env['hr.leave.type'].sudo().get_days_all_request(),
        }
        return request.render("hr_portal_timeoff.portal_my_leave_edit", values)



    def update_my_leave(self, form_data, **kw):
        if form_data['leave_id']:
            leave = request.env['hr.leave'].sudo().browse(form_data['leave_id'])
            leave.sudo().write({
                    'name': form_data['description'],
                    'holiday_status_id': form_data['holiday_status_id'],
                    'request_date_from': form_data['request_from_date'],
                    'request_date_to': form_data['request_to_date'],
                    'employee_id': form_data['employee_id'],
                    'request_unit_half': form_data['half_day'],
                    'number_of_days': form_data['number_of_days'],
                    'request_unit_hours': form_data['request_unit_hours'],
                    'request_hour_from': form_data['request_hours_from'],
                    'request_hour_to': form_data['request_hours_to'],
                    'date_from': form_data['date_from'],
                    'date_to': form_data['date_to'],
                })
        return leave

    @http.route(['/portal/timeoff/update/'], type='json', auth="user")
    def update_my_timeoff(self, form_data, **kw):
        holiday_status_id = request.env['hr.leave.type'].sudo().browse(form_data['holiday_status_id'])

        leave_days = holiday_status_id.get_days(form_data['employee_id'])[holiday_status_id.id]
        if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
            raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                                    'Please also check the time off waiting for validation.'))
        if leave_days['remaining_leaves'] < form_data['number_of_days'] or leave_days['virtual_remaining_leaves'] < form_data['number_of_days']:
            raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                                    'Please also check the time off waiting for validation.'))

        leave = self.update_my_leave(form_data, **kw)
        return {'leave_id': leave,'write_date':leave.write_date,'error': 0,}



    #team timeoff block
    @http.route(['/my/team/leaves', '/my/team/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_team_timeoff(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='Employee', **kw):
        Timeoff_sudo = request.env['hr.leave'].sudo()
        values = self._prepare_portal_layout_values()
        domain = [('employee_id.timeoff_portal_manager_id', '=' , request.env.user.id)]

        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'Time Off Type': {'input': 'holiday_status_id', 'label': _('Time Off Type')},
            'Employee': {'input': 'employee_id', 'label': _('Employee')},
        }

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("create_date", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('create_date', '>=', date_utils.start_of(today, "week")), ('create_date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('create_date', '>=', date_utils.start_of(today, 'month')), ('create_date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('create_date', '>=', date_utils.start_of(today, 'year')), ('create_date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('create_date', '>=', quarter_start), ('create_date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('create_date', '>=', date_utils.start_of(last_week, "week")), ('create_date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('create_date', '>=', date_utils.start_of(last_month, 'month')), ('create_date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('create_date', '>=', date_utils.start_of(last_year, 'year')), ('create_date', '<=', date_utils.end_of(last_year, 'year'))]},
        }
        # default sort by value
        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain = AND([domain, [('name', 'ilike', search)]])

        timeoff_count = Timeoff_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/team/leaves",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=timeoff_count,
            page=page,
            step=self._items_per_page
        )

        if groupby == 'Time Off Type':
            order = "holiday_status_id, %s" % order
        if groupby == 'Employee':
            order = "employee_id, %s" % order
        timeoffs = Timeoff_sudo.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'Time Off Type':
            grouped_leaves = [Timeoff_sudo.concat(*g) for k, g in groupbyelem(timeoffs, itemgetter('holiday_status_id'))]
        elif groupby == 'Employee':
            grouped_leaves = [Timeoff_sudo.concat(*g) for k, g in groupbyelem(timeoffs, itemgetter('employee_id'))]
        else:
            grouped_leaves = [timeoffs]

        values.update({
            'timeoffs': timeoffs,
            'grouped_leaves': grouped_leaves,
            'page_name': 'my_team_leaves',
            'default_url': '/my/team/leaves',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("hr_portal_timeoff.portal_my_team_leaves", values)


    @http.route(['/my/team/leaves/approve/'], type='json', auth="user")
    def action_approve_portal_timeoff(self, leave_id, **kw):
        if leave_id:
            leave = request.env['hr.leave'].sudo().browse(leave_id)
            result = leave.sudo().action_approve()
            if result:
                return {'leave_id': leave, 'error': 0,}



    @http.route(['/my/team/leaves/refuse/'], type='json', auth="user")
    def action_refuse_portal_timeoff(self,review, leave_id, **kw):
        if leave_id:
            leave = request.env['hr.leave'].sudo().browse(leave_id)
            result = leave.action_refuse()

            if result:
                leave.sudo().write({'report_note':review})

                return {'leave_id': leave, 'error': 0,}

