
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter

from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND
from werkzeug.wsgi import get_current_url

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class AttendanceCustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(AttendanceCustomerPortal, self)._prepare_portal_layout_values()
        # domain = request.env['hr.attandance']._attendance_get_portal_domain()
        values['attendance_count'] = request.env['hr.attendance'].sudo().search_count([('employee_id.user_id','=',request.env.user.id)])
        return values

    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendances(self, page=1, sortby=None, filterby=None, search=None, search_in='all',  **kw):
        attendance_sudo = request.env['hr.attendance'].sudo()
        values = self._prepare_portal_layout_values()
        domain = [('employee_id.user_id','=',request.env.user.id)]

        employee = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        
        attendance_count = attendance_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/attendance",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )


        attendances = attendance_sudo.search(domain, limit=self._items_per_page, offset=pager['offset'])
        grouped_attendances = [attendances]

        values.update({
            'attendances': attendances,
            'grouped_attendances': grouped_attendances,
            'page_name': 'attendance',
            'default_url': '/my/attendance',
            'pager': pager,
            'logged_in_user':request.env.user.id,
            'employee':employee,

            
        })
        return request.render("hr_portal_attendance.portal_my_attendance", values)
