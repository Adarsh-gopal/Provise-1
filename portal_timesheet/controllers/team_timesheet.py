# -*- coding: utf-8 -*-
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import calendar
import datetime
from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
import itertools
from odoo.osv.expression import AND
from werkzeug.wsgi import get_current_url
from odoo.exceptions import AccessError, UserError, ValidationError, Warning
from odoo.tools.translate import _
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.osv import expression
import ast 
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.sale_timesheet_enterprise.models.sale import DEFAULT_INVOICED_TIMESHEET


class TeamTimesheetCustomerPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(TeamTimesheetCustomerPortal, self)._prepare_portal_layout_values()
        values['team_employees_count'] = request.env['account.analytic.line'].sudo().search_count([('employee_id.timesheet_portal_manager_id', '=' , request.env.user.id)])
        values['is_timesheet_manager'] = True if request.env.user.has_group('portal_timesheet.group_hr_timesheet_portal_approver') else False
       
        return values


    #team timeoff block
    @http.route(['/my/team/timesheets', '/my/team/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_team_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='project', **kw):
        Timesheet_sudo = request.env['account.analytic.line'].sudo()
        values = self._prepare_portal_layout_values()
        domain = [('employee_id.timesheet_portal_manager_id', '=' , request.env.user.id)]
        # param_invoiced_timesheet = request.env['ir.config_parameter'].sudo().get_param('sale.invoiced_timesheet', DEFAULT_INVOICED_TIMESHEET)
        # if param_invoiced_timesheet == 'approved':
        #     domain = expression.OR([domain, [('validated', '=', False)]])
        # if param_invoiced_timesheet == 'all':
        #     domain = expression.AND([domain, ['|',('validated', '=', False),('validated', '=', True)]])
        # if not request.env.user.has_group('hr_timesheet.group_hr_timesheet_user') or not request.env.user.has_group('hr_timesheet.group_hr_timesheet_approver') or not request.env.user.has_group('hr_timesheet.group_timesheet_manager') :
        #     domain = expression.AND([domain, [('employee_id.timesheet_portal_manager_id', '=' , request.env.user.id)]])

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project': {'input': 'project', 'label': _('Project')},
            'employee': {'input': 'employee_id', 'label': _('Employee')},
        }

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('date', '>=', date_utils.start_of(today, "week")), ('date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date', '>=', date_utils.start_of(today, 'month')), ('date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date', '>=', date_utils.start_of(today, 'year')), ('date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('date', '>=', quarter_start), ('date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date', '>=', date_utils.start_of(last_week, "week")), ('date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('date', '>=', date_utils.start_of(last_month, 'month')), ('date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date', '>=', date_utils.start_of(last_year, 'year')), ('date', '<=', date_utils.end_of(last_year, 'year'))]},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain = AND([domain, [('name', 'ilike', search)]])

        if groupby == 'project':
            order = "project_id, %s" % order
        if groupby == 'employee':
            order = "employee_id, %s" % order
        # pager
        timesheets = Timesheet_sudo.search(domain, order=order)


        grp_by_month = []
        for line in timesheets:
            if not (line.employee_id, line.date.strftime('%b %Y'), line.project_id) in grp_by_month:
                grp_by_month.append((line.employee_id, line.date.strftime('%b %Y'), line.project_id))

        timesheet_count = len(grp_by_month)

        # print(grp_by_month,)


        pager = portal_pager(
            url="/my/team/timesheets",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby, 'groupby' : groupby},
            total=timesheet_count,
            page=page,
            step=self._items_per_page
        )


        if groupby == 'project':
            grouped_timesheets = [list(g) for k, g in itertools.groupby(grp_by_month, lambda x: x[2].name)]
        elif groupby == 'employee':
            grouped_timesheets = [list(g) for k, g in itertools.groupby(grp_by_month, lambda x: x[0].name)]
        else:
            grouped_timesheets = [grp_by_month]


        values.update({
            'timesheets': timesheets,
            'grp_month':Timesheet_sudo,
            'grouped_timesheets': grouped_timesheets,
            'page_name': 'team_timesheet',
            'default_url': '/my/team/timesheets',
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
        return request.render("portal_timesheet.portal_my_team_timesheets", values)



    @http.route(['/my/team/timesheets/<int:employee_id>/<int:project_id>/<int:month>/<int:year>', '/my/team/timesheets/<int:employee_id>/<int:project_id>/<int:month>/<int:year>/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_team_timesheets_by_month(self,  employee_id, project_id, month, year, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='project', **kw):
        Timesheet_sudo = request.env['account.analytic.line'].sudo()
        mnth_rg = calendar.monthrange(year, month)
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, mnth_rg[1])
        project = request.env['project.project'].sudo().browse(project_id)
        employee = request.env['hr.employee'].sudo().browse(employee_id)

        values = self._prepare_portal_layout_values()
        domain = [('employee_id', '=' , employee_id),('project_id', '=' , project_id),('project_id', '=' , project_id),('date','>=', start_date),('date','<=',end_date)]
        # param_invoiced_timesheet = request.env['ir.config_parameter'].sudo().get_param('sale.invoiced_timesheet', DEFAULT_INVOICED_TIMESHEET)
        # if param_invoiced_timesheet == 'approved':
        #     domain = expression.OR([domain, [('validated', '=', False)]])
        # if param_invoiced_timesheet == 'all':
        #     domain = expression.AND([domain, ['|',('validated', '=', False),('validated', '=', True)]])
        # if not request.env.user.has_group('hr_timesheet.group_hr_timesheet_user') or not request.env.user.has_group('hr_timesheet.group_hr_timesheet_approver') or not request.env.user.has_group('hr_timesheet.group_timesheet_manager') :
        #     domain = expression.AND([domain, [('employee_id.user_id', '=' , request.env.user.id)]])

        timesheets = Timesheet_sudo.search(domain)

      
        grouped_timesheets = [timesheets]

        values.update({
            'timesheets': timesheets,
            # 'grouped_timesheets': grouped_timesheets,
            'period':start_date,
            'page_name': 'tmsh_by_month',
            'project_id':project,
            'employee_id':employee,
        })
        return request.render("portal_timesheet.team_timesheet_by_month_portal", values)


    @http.route(['/my/team/timesheet/approve/'], type='json', auth="user")
    def action_approve_portal_timesheet(self, timesheet_id, **kw):
        if timesheet_id:
            timesheet = request.env['account.analytic.line'].sudo().browse(timesheet_id)
            result = timesheet.sudo().write({'manager_approval_state':'approved'})
            if result:
                return {'timesheet_id': timesheet, 'error': 0,}     



    @http.route(['/my/team/timesheet/approve_all/'], type='json', auth="user")
    def action_approve_portal_all_timesheet(self, timesheet_ids, **kw):
        if timesheet_ids:
            tm_ids_list = ast.literal_eval(timesheet_ids)
            tmsh= request.env['account.analytic.line'].sudo().search([('id','in',tm_ids_list)])

            approved = tmsh.filtered(lambda x: x.manager_approval_state == 'pending_approval')
            if not approved:
                raise Warning('There is no timesheet to Approve')

            validated = tmsh.filtered(lambda x: x.validated == False)
            if not validated:
                raise Warning('You can\'t approve validated timesheets')


            for rec in tmsh:
                if rec.manager_approval_state == 'pending_approval' and rec.validated == False:
                    rec.sudo().write({'manager_approval_state':'approved'})

            return {'timesheet_id': tmsh, 'error': 0,}


    # @http.route(['/my/team/timesheet/resubmit/'], type='json', auth="user")
    # def action_resubmit_portal_timesheet(self, timesheet_id, **kw):
    #     if timesheet_id:
    #         timesheet = request.env['account.analytic.line'].sudo().browse(timesheet_id)
    #         result = timesheet.sudo().write({'manager_approval_state':'resubmit'})
    #         if result:
    #             return {'timesheet_id': timesheet, 'error': 0,} 


    @http.route(['/my/team/timesheet/resubmit_all/'], type='json', auth="user")
    def action_resubmit_portal_all_timesheets(self, timesheet_ids, **kw):
        if timesheet_ids:
            tm_ids_list = ast.literal_eval(timesheet_ids)
            tmsh= request.env['account.analytic.line'].sudo().search([('id','in',tm_ids_list)])

            approved = tmsh.filtered(lambda x: x.manager_approval_state == 'approved')
            if not approved:
                raise Warning('There is no timesheet to resubmit')

            # validated = tmsh.filtered(lambda x: x.validated == False)
            # if not validated:
            #     raise Warning('You can\'t approve validated timesheets')


            for rec in tmsh:
                if rec.manager_approval_state == 'approved' and rec.validated == False:
                    rec.sudo().write({'manager_approval_state':'resubmit'})

            return {'timesheet_id': tmsh, 'error': 0,}   



    @http.route(['/my/team/timesheet/resubmit/'], type='json', auth="user")
    def action_refuse_portal_timesheet(self,review, timesheet_id, **kw):
        if timesheet_id:
            tm = request.env['account.analytic.line'].sudo().browse(timesheet_id)
            result = tm.sudo().write({'resubmit_reason':review,'manager_approval_state':'resubmit'})

            if result:
                return {'timesheet_id': tm, 'error': 0,}