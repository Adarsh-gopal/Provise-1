from odoo import fields, http, models, _
from odoo.exceptions import AccessError, UserError, ValidationError, Warning
from odoo.tools import consteq
from odoo.http import request
from odoo.osv import expression
from collections import OrderedDict
from operator import itemgetter
import itertools
from dateutil.relativedelta import relativedelta
from odoo.addons.project.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import  pager as portal_pager
from werkzeug.wsgi import get_current_url
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND
import ast 

from odoo.addons.sale_timesheet_enterprise.models.sale import DEFAULT_INVOICED_TIMESHEET


class ProjectCustomerPortal(CustomerPortal):

    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = super(ProjectCustomerPortal, self)._task_get_page_view_values(task, access_token, **kwargs)
        values['delivery_sites'] = request.env['delivery.sites'].sudo().search([])
        values['projects'] = request.env['project.project'].sudo().search([])
        values['tasks'] = request.env['project.task'].sudo().search([])
        values['original_link'] = get_current_url(request.httprequest.environ)
        domain = request.env['account.analytic.line']._timesheet_get_portal_domain()
        param_invoiced_timesheet = request.env['ir.config_parameter'].sudo().get_param('sale.invoiced_timesheet', DEFAULT_INVOICED_TIMESHEET)
        if param_invoiced_timesheet == 'approved':
            domain = expression.OR([domain, [('validated', '=', False)]])
        if param_invoiced_timesheet == 'all':
            domain = expression.AND([domain, ['|',('validated', '=', False),('validated', '=', True)]])
        domain = expression.AND([domain, [('task_id', '=', task.id)]])

        timesheets = request.env['account.analytic.line'].sudo().search(domain)
        values['timesheets'] = timesheets
        return values

    def update_timesheet_task(self, form_data, **kw):
        emp = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)],limit=1)
        if not emp:
            raise Warning('Employee is not assigned for this User! Please Contact Admnistrator...')


        if form_data['task_id']:
            task = request.env['project.task'].sudo().browse(form_data['task_id'])
            prepare_timesheet_ids = {
                    'date' : form_data['date'],
                    'employee_id': request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)],limit=1).id,
                    'name' : form_data['description'],
                    'status' : form_data['status'],
                    'delivery_site' : form_data['delivery_site'],
                    'unit_amount': form_data['unit_amount'],
                    # 'unit_amount': float((form_data['unit_amount']).replace(':','.')),
                    'account_id': task.project_id.analytic_account_id.id,
                    'project_id': task.project_id.id,
                    'manager_approval_state':'pending_submission',
                    # 'product_uom_id':task.sale_line_id.product_uom.id,

                }
            task_timesheet = task.write({'timesheet_ids': [(0,0,prepare_timesheet_ids)] })

        return task_timesheet

    @http.route(['/portal/timesheet/submit/'], type='json', auth="user")
    def submit_timesheet(self, form_data, **kw):
        time_sheet_data = self.update_timesheet_task(form_data, **kw)

        return {'timesheet_id': time_sheet_data,'error': 0,}



    @http.route(['/my/task/<int:task_id>/<int:timesheet_id>'], type='http', auth="public", website=True)
    def portal_my_task_timesheet_edit(self, task_id, timesheet_id, access_token=None, **kw):
        if timesheet_id:
            timesheet = request.env['account.analytic.line'].sudo().browse(timesheet_id)
        # values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        values = {
            'page_name' : 'edit_timesheet',
            'timesheet':timesheet,
            'delivery_sites' : request.env['delivery.sites'].sudo().search([]),
            'projects' : request.env['project.project'].sudo().search([]),
            'tasks' : request.env['project.task'].sudo().search([]),
        }
        return request.render("portal_timesheet.portal_my_task_timesheet_edit", values)


    def write_form_data(self, form_data, **kw):
        if form_data['timesheet_id']:
            timesheet = request.env['account.analytic.line'].sudo().browse(form_data['timesheet_id'])
            timesheet.sudo().write({
                    'date' : form_data['date'],
                    'name' : form_data['description'],
                    'status' : form_data['status'],
                    'delivery_site' : form_data['delivery_site'],
                    'unit_amount': form_data['unit_amount'],
                    'manager_approval_state':'pending_submission',
                    # 'unit_amount': float((form_data['unit_amount']).replace(':','.')),
                })
        return timesheet

    @http.route(['/portal/timesheet/update/'], type='json', auth="user")
    def update_timesheet(self, form_data, **kw):
        timesheet = self.write_form_data(form_data, **kw)
        return {'timesheet_id': timesheet,'write_date':timesheet.write_date,'error': 0,}



    def _prepare_portal_layout_values(self):
        values = super(ProjectCustomerPortal, self)._prepare_portal_layout_values()
        if request.env.user.id == 2:
            dn = []
        else:
            dn = [('user_id','=',request.env.user.id)]
        values['task_count'] = request.env['project.task'].sudo().search_count(dn)
        return values



  


    @http.route()
    def portal_my_tasks(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby='project', **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'stage': {'input': 'stage', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project': {'input': 'project', 'label': _('Project')},
        }

        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].search([])
        for project in projects:
            searchbar_filters.update({
                str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
            })

        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        project_groups = request.env['project.task'].read_group([('project_id', 'not in', projects.ids)],
                                                                ['project_id'], ['project_id'])
        for group in project_groups:
            proj_id = group['project_id'][0] if group['project_id'] else False
            proj_name = group['project_id'][1] if group['project_id'] else _('Others')
            searchbar_filters.update({
                str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
            })

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('project.task', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        if not request.env.user.id == 2:
            domain += [('user_id','=',request.env.user.id)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            if search_in in ('stage', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        # task count
        task_count = request.env['project.task'].search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tasks",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        if groupby == 'project':
            order = "project_id, %s" % order  # force sort on project first to group by project in view
        tasks = request.env['project.task'].search(domain, order=order, limit=self._items_per_page, offset=(page - 1) * self._items_per_page)
        request.session['my_tasks_history'] = tasks.ids[:100]
        if groupby == 'project':
            grouped_tasks = [request.env['project.task'].concat(*g) for k, g in groupbyelem(tasks, itemgetter('project_id'))]
        else:
            grouped_tasks = [tasks]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'page_name': 'task',
            'archive_groups': archive_groups,
            'default_url': '/my/tasks',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("project.portal_my_tasks", values)


    @http.route(['/my/task/<int:task_id>','/my/task/<int:task_id>/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_task(self, task_id, access_token=None, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='month', **kw):
        try:
            task_sudo = self._document_check_access('project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        Timesheet_sudo = request.env['account.analytic.line'].sudo()
        domain = request.env['account.analytic.line']._timesheet_get_portal_domain()
        param_invoiced_timesheet = request.env['ir.config_parameter'].sudo().get_param('sale.invoiced_timesheet', DEFAULT_INVOICED_TIMESHEET)
        if param_invoiced_timesheet == 'approved':
            domain = expression.OR([domain, [('validated', '=', False)]])
        if param_invoiced_timesheet == 'all':
            domain = expression.AND([domain, ['|',('validated', '=', False),('validated', '=', True)]])
        domain = expression.AND([domain, [('task_id', '=', task_id)]])

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'month': {'input': 'month', 'label': _('Month')},
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

        timesheet_count = Timesheet_sudo.search_count(domain)
        # pager
        # pager = portal_pager(
        #     url="/my/task/%d" %task_id,
        #     # url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
        #     total=timesheet_count,
        #     page=page,
        #     step=self._items_per_page
        # )

        if groupby == 'month':
            order = "date, %s" % order
        timesheets = Timesheet_sudo.search(domain, order=order)
        if groupby == 'month':
            grouped_tms = [Timesheet_sudo.concat(*g) for k, g in itertools.groupby(timesheets, lambda x: x.date.month)]
        else:
            grouped_tms = [timesheets]


        # ensure attachment are accessible with access token inside template
        for attachment in task_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self._task_get_page_view_values(task_sudo, access_token, **kw)

        values.update({
        'grouped_tms': grouped_tms,
        # 'pager': pager,
        'default_url': '/my/task/%d' %task_id,
        'searchbar_sortings': searchbar_sortings,
        'search_in': search_in,
        'sortby': sortby,
        'groupby': groupby,
        'searchbar_inputs': searchbar_inputs,
        'searchbar_groupby': searchbar_groupby,
        'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        'filterby': filterby,
        })
        return request.render("project.portal_my_task", values)



    @http.route(['/portal/timesheet/submit_all/'], type='json', auth="user")
    def submit_all_tm_for_approval(self, timesheet_ids, **kw):
        tm_ids_list = ast.literal_eval(timesheet_ids)
        if not tm_ids_list:
            error = 1
            # raise Warning('There is no Timesheets for Submission ')
        else:
            tmsh= request.env['account.analytic.line'].sudo().search([('id','in',tm_ids_list)])

            for rec in tmsh:
                if rec.manager_approval_state == 'pending_submission' and rec.validated == False:
                    rec.sudo().write({'manager_approval_state':'pending_approval'})
            error = 0

        return {'error': error}