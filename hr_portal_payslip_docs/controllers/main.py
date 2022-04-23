# -*- coding: utf-8 -*-
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from odoo.exceptions import Warning, UserError, AccessError,AccessDenied
from odoo.tools import safe_eval
from odoo import fields, http, _
from odoo.http import request,  content_disposition
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND
from werkzeug.wsgi import get_current_url

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class PayslipPortalDocument(CustomerPortal):

    @http.route(['/report/pdf/payslip_download'], type='http', auth='user')
    def payslip_download(self, payslip_id, fandf=False):
        pay_slip = request.env['hr.payslip'].sudo().browse(int(payslip_id))
        if pay_slip.employee_id.user_id.id != request.env.user.id or pay_slip.state != 'done':
            raise AccessDenied('You can\'t access this Appraisal document')
        report_name = pay_slip.name

        if safe_eval(fandf):
            report_id = request.env['ir.config_parameter'].sudo().get_param('hr_portal_payslip_docs.fndf_payslip_report_template')
            if not report_id:
                raise AccessDenied('Full and Final settlement Report not selected in Backend, please contact HR')
        else:
            report_id = request.env['ir.config_parameter'].sudo().get_param('hr_portal_payslip_docs.payslip_report_template')

        if report_id:
            report_action = request.env['ir.actions.report'].sudo().browse(int(report_id))
        else:
            report_action = http.request.env.ref('hr_payroll.action_report_payslip').sudo()
        pdf_content, _ = report_action.render_qweb_pdf(int(payslip_id))
   
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', u'%s' % len(pdf_content)),
            ('Content-Disposition', content_disposition(report_name + '.pdf')),
        ]
        return request.make_response(pdf_content, headers=pdfhttpheaders)



    def _prepare_portal_layout_values(self):
        values = super(PayslipPortalDocument, self)._prepare_portal_layout_values()
        values['payslip_counts'] = request.env['hr.payslip'].sudo().search_count([('employee_id.user_id', '=' , request.env.user.id)])
        values['original_link'] = get_current_url(request.httprequest.environ)
        return values

    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def portal_payslip(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):
        Payslip_sudo = request.env['hr.payslip'].sudo()
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
            # 'Time Off Type': {'input': 'holiday_status_id', 'label': _('Time Off Type')},
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

        payslips_count = Payslip_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/payslips",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=payslips_count,
            page=page,
            step=self._items_per_page
        )

        # if groupby == 'Time Off Type':
        #     order = "holiday_status_id, %s" % order
        payslips = Payslip_sudo.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        # if groupby == 'Time Off Type':
        #     grouped_payslips = [Payslip_sudo.concat(*g) for k, g in groupbyelem(payslips, itemgetter('holiday_status_id'))]
        # else:
        grouped_payslips = [payslips]

        report_templates = False
        if request.env['ir.config_parameter'].sudo().get_param('hr_portal_payslip_docs.fndf_payslip_report_template') and request.env['ir.config_parameter'].sudo().get_param('hr_portal_payslip_docs.payslip_report_template'):
            report_templates = True

        values.update({
            'payslips': payslips,
            'grouped_payslips': grouped_payslips,
            'report_templates': report_templates,
            'page_name': 'my_payslips',
            'default_url': '/my/payslips',
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
        return request.render("hr_portal_payslip_docs.portal_my_payslip", values)