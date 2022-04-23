# -*- coding: utf-8 -*-
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from odoo.exceptions import Warning, UserError, AccessError,AccessDenied,ValidationError
from odoo.tools import safe_eval
from odoo import fields, http, _
from odoo.http import request,  content_disposition
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND
from werkzeug.wsgi import get_current_url
from datetime import date

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class HrPortalAppraisal(CustomerPortal):

    @http.route(['/report/pdf/appraisal_download'], type='http', auth='user')
    def appraisal_download(self, appraisal_id, fandf=False):
        appraisal = request.env['hr.appraisal'].sudo().browse(int(appraisal_id))
        if appraisal.employee_id.user_id.id != request.env.user.id or appraisal.state != 'approved':
            raise AccessDenied('You can\'t access this Appraisal document')

        report_name = appraisal.employee_id.name
        report_id = request.env['ir.config_parameter'].sudo().get_param('hr_portal_appraisal.appraisal_report_template')

        if report_id:
            report_action = request.env['ir.actions.report'].sudo().browse(int(report_id))
        else:
            raise AccessDenied('There is reports Selected.!! Please Contact HR')

        pdf_content, _ = report_action.render_qweb_pdf(int(appraisal_id))
   
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', u'%s' % len(pdf_content)),
            ('Content-Disposition', content_disposition(report_name + '.pdf')),
        ]
        return request.make_response(pdf_content, headers=pdfhttpheaders)

    def _prepare_portal_layout_values(self):
        values = super(HrPortalAppraisal, self)._prepare_portal_layout_values()
        values['self_appraisal_count'] = request.env['hr.appraisal'].sudo().search_count([('employee_id.user_id', '=' , request.env.user.id),('state','!=','new')])
        values['original_link'] = get_current_url(request.httprequest.environ)
        emp_id = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        values['team_appraisal_count'] = request.env['hr.appraisal'].sudo().search_count([('employee_id.parent_id', '=' , emp_id.id),('employee_assessment','!=',False)])
        return values

    @http.route(['/my/appraisals', '/my/appraisals/page/<int:page>'], type='http', auth="user", website=True)
    def portal_appraisal(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):

        # if kw.get('success'):
        #     print(kw.get('success'),'&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')

        Appraisal_sudo = request.env['hr.appraisal'].sudo()
        values = self._prepare_portal_layout_values()
        domain = [('employee_id.user_id', '=' , request.env.user.id),('state','!=','new')]

        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'employee_id'},
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

        appraisal_count = Appraisal_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/appraisals",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=appraisal_count,
            page=page,
            step=self._items_per_page
        )

        # if groupby == 'Time Off Type':
        #     order = "holiday_status_id, %s" % order
        appraisals = Appraisal_sudo.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        # if groupby == 'Time Off Type':
        #     grouped_appraisals = [Appraisal_sudo.concat(*g) for k, g in groupbyelem(appraisals, itemgetter('holiday_status_id'))]
        # else:
        grouped_appraisals = [appraisals]
        employee_id = request.env['hr.employee'].sudo().search([('user_id','=', request.env.user.id)])

        values.update({
            'appraisals': appraisals,
            'grouped_appraisals': grouped_appraisals,
            'page_name': 'my_appraisals',
            'default_url': '/my/appraisals',
            'employee_id':employee_id.id,
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
        return request.render("hr_portal_appraisal.portal_my_appraisal", values)



    @http.route(['/my/appraisals/self-assessment/<int:appraisal_id>'], type='http', auth="user", website=True)
    def appraisal_self_assement(self, appraisal_id, access_token=None, **kw):
        if appraisal_id:
            appraisal = request.env['hr.appraisal'].sudo().browse(appraisal_id)
        # values = self._task_get_page_view_values(task_sudo, access_token, **kw)

        # if appraisal:
        #     if appraisal.state not in ['draft','confirm']:
        #         return request.redirect('/my/appraisals')
        emp_id = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        if not appraisal.employee_id.id == emp_id.id or appraisal.employee_assessment:
            raise AccessDenied('You are not suppose to access this page')

        values = {
            'page_name' : 'self_assessment',
            'appraisal':appraisal,
        }
        return request.render("hr_portal_appraisal.appraisal_self_assessment", values)

    def update_employee_assessment(self, form_data, **kw):
        if form_data['appraisal_id']:
            apprl = request.env['hr.appraisal'].sudo().browse(form_data['appraisal_id'])
            employee_assessment_data = {
                        'tab_ans1':apprl.employee_id.name or '', 
                        'tab_ans2':apprl.employee_id.registration_number or '',
                        'tab_ans3':apprl.employee_id.date_of_joining or '',
                        'tab_ans4':apprl.employee_id.job_id.name or '',
                        'tab_ans5':apprl.employee_id.project_id.partner_id.name or '',
                        'tab_ans6':apprl.appraisal_period.name or '',
                        'tab_ans7':apprl.employee_id.parent_id.name or '',
                        'tab_ans8':apprl.create_date or '',  
                        'tab_ans9':apprl.employee_assessment_submit_date or '',  
                        'ques1': form_data['ques1'] or ' ',
                        'ques2': form_data['ques2'] or ' ',
                        'ques3': form_data['ques3'] or ' ',
                        'ques4': form_data['ques4'] or ' ',
                        'ques5_1': form_data['ques5_1'] or ' ',
                        'ques5_2': form_data['ques5_2'] or ' ',
                        'ques5_3': form_data['ques5_3'] or ' ',
                        'ques5_4': form_data['ques5_4'] or ' ',
                        'pdp_ques1_1': form_data['pdp_ques1_1'] or ' ',
                        'pdp_ques1_2': form_data['pdp_ques1_2'] or ' ',
                        'pdp_ques2': form_data['pdp_ques2'] or ' ',
                        'pdp_ques3_1': form_data['pdp_ques3_1'] or ' ',
                        'pdp_ques3_2': form_data['pdp_ques3_2'] or ' ',
                        'pdp_ques3_3': form_data['pdp_ques3_3'] or ' ',
                        }


            html_data = """ 
                    <div class="row">
                        <div class="col-md-6 offset-md-3">
                            <table class="table table-sm table-bordered">
                                <tr>
                                    <td><strong>Employee Name:</strong></td><td>%(tab_ans1)s</td>
                                </tr>
                                <tr>
                                    <td><strong>Employee IEN (Instellars Employee No.):</strong></td><td>%(tab_ans2)s</td>
                                </tr>
                                <tr>
                                    <td><strong>Date of Joining IGC:</strong></td><td>%(tab_ans3)s</td>
                                </tr>
                                <tr>
                                    <td><strong>Designation:</strong></td><td>%(tab_ans4)s</td>
                                </tr>
                                <tr>
                                    <td><strong>Client Name</strong></td><td>%(tab_ans5)s</td>
                                </tr>
                                <tr>
                                    <td><strong>Assessment Period</strong></td><td>%(tab_ans6)s</td>
                                </tr>
                                <tr>
                                    <td><strong>Name of Counselor</strong></td><td>%(tab_ans7)s</td>
                                </tr>
                                <tr>
                                    <td><strong>Date of Issue of Form:</strong></td><td>%(tab_ans8)s</td>
                                </tr>
                                <tr>
                                    <td><strong>Date of Submission(to Counselor) of Form:</strong></td><td>%(tab_ans9)s</td>
                                </tr>
                            </table>
                        </div>
                    </div>
            <div class="row" style="color:#000000">
                <div class="col-lg-8 offset-lg-2 mb8 pull-left">
                    <h5 class="mb16 mt16 text-center" style="background-color: #2b2554;color: white;padding: 7px;"> Self Assessment Form</h5>
                    <p style="text-align:justify">
                        To be filled in and submitted by the Counselee to the Counselor prior to the one on one discussion. The counselee should fill up self-assessment form based on evidence, facts and self-observations on demonstration.
                    </p>
                </div>

                <div class="form-group col-lg-8 offset-lg-2 pull-left">
                    <label class="control-label" for="ques1"><strong>1. What is your current role and briefly describe your responsibilities?</strong></label>
                    <p>%(ques1)s</p>
                </div>
                <div class="form-group col-lg-8 offset-lg-2 pull-left">
                    <label class="control-label" for="ques2"><strong>2. How do you see your current role vis-à-vis your own career goal?</strong></label>
                    <p>%(ques2)s</p>
                </div>
                <div class="form-group col-lg-8 offset-lg-2 pull-left">
                    <label class="control-label" for="ques3"><strong>3. What according to you are the top three strengths that you demonstrate in your current role?</strong></label>
                    <p>%(ques3)s</p>
                </div>
                <div class="form-group col-lg-8 offset-lg-2 pull-left">
                    <label class="control-label" for="ques4"><strong>4. What according to you are your top three areas of improvement in your current role? (E.g. knowledge, skills, etc.)</strong></label>
                    <p>%(ques4)s</p>
                </div>
                <div class="form-group col-lg-8 offset-lg-2 pull-left">
                    <label class="control-label" for="ques5"><strong>5. Mention any significant contribution you made towards the following areas. Please support with examples.</strong></label>
                    <table class="table table-sm table-bordered">
                        <tr>
                            <th>Knowledge Sharing:</th>
                            <td><p>%(ques5_1)s</p></td>
                        </tr>
                        <tr>
                            <th> Developing Others:</th>
                            <td><p>%(ques5_2)s</p></td>
                        </tr><tr>
                            <th>Improving process efficiency (Innovation/ cost saving ideas, etc.):</th>
                            <td><p>%(ques5_3)s</p></td>
                        </tr>
                        <tr>
                            <th>Any other: (Please specify)</th><td><p>%(ques5_4)s</p></td>
                        </tr>
                    </table>
                </div>
                <div class="col-lg-8 offset-lg-2 mb8 pull-left">
                    <h5 class="mb16 mt16 text-center" style="background-color: #2b2554;color: white;padding: 7px;">Personal Development Plan</h5>
                    <p style="text-align:justify">
                        The Personal Development Plan (PDP) documents the short term and long-term learning activities that a Counselee plans to accomplish. This is to further develop the competencies (knowledge/ skills etc) required to successfully achieve current job standards and further career development. Competencies identified for professional development should relate to the counselee’s job assignments and/ or to career aspirations for the short and long term.
                    </p>
                </div>
                <div class="form-group col-lg-8 offset-lg-2 pull-left">
                    <table class="table table-sm table-bordered">
                        <tr>
                            <td>
                                <div class="form-group col-lg-12 pull-left">
                                    <label class="control-label" for="pdp_ques1"><strong>1. What is your career goal in:</strong></label>
                                </div>
                                <div class="form-group col-lg-6 pull-left">
                                    <label class="control-label" for="pdp_ques1_1"><strong>Short Term:(1-2 years):</strong></label>
                                    <p>%(pdp_ques1_1)s</p>
                                </div>
                                <div class="form-group col-lg-6 pull-left">
                                    <label class="control-label" for="pdp_ques1_2"> <strong>Long Term:(2-4 years):</strong></label>
                                    <p>%(pdp_ques1_2)s</p>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="form-group col-lg-12 pull-left">
                                    <label class="control-label" for="pdp_ques2"><strong>2. What training/ coaching inputs you would require so as to enhance your performance in your current role? </strong></label>
                                    <p>%(pdp_ques2)s</p>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="form-group col-lg-12 pull-left">
                                    <label class="control-label" for="pdp_ques3"><strong>3. What support would you require for further enhancing your performance in your current role?</strong></label>
                                </div>
                                <div class="form-group col-lg-12 pull-left">
                                    <label class="control-label"><strong>    a. From your Counselor: </strong></label>
                                    <p>%(pdp_ques3_1)s</p>
                                </div>
                                 <div class="form-group col-lg-12 pull-left">
                                      <label class="control-label"><strong>  b. From your team members:</strong> </label>
                                      <p>%(pdp_ques3_2)s</p>
                                </div>
                                 <div class="form-group col-lg-12 pull-left">
                                      <label class="control-label"><strong>  c. Others (please specify):</strong></label>
                                      <p>%(pdp_ques3_3)s</p>
                                </div>  
                            </td>
                        </tr>
                    </table>
                </div>
            </div>

            """%(employee_assessment_data)

        if form_data['appraisal_id']:
            app = request.env['hr.appraisal'].sudo().browse(form_data['appraisal_id'])
            app.write({'employee_assessment':html_data,'employee_assessment_submit_date':fields.datetime.today()})

            return app



    @http.route(['/self_assessment/form/submit/'], type='json', auth="user")
    def submit_self_assessment(self, form_data, **kw):
        appraisal = self.update_employee_assessment(form_data, **kw)
        return {'appraisal_id': appraisal,'error': 0,}



    #team assessment block 

    @http.route(['/my/team/appraisals', '/my/team/appraisals/page/<int:page>'], type='http', auth="user", website=True)
    def my_team_portal_appraisal(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='employee', **kw):
        Appraisal_sudo = request.env['hr.appraisal'].sudo()
        values = self._prepare_portal_layout_values()
        emp_id = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        domain = [('employee_id.parent_id', '=' , emp_id.id),('employee_assessment','!=',False)]

        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'employee_id'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'employee': {'input': 'employee_id', 'label': _('Employee')},
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

        appraisal_count = Appraisal_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/team/appraisals",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=appraisal_count,
            page=page,
            step=self._items_per_page
        )

        if groupby == 'employee':
            order = "employee_id, %s" % order
        appraisals = Appraisal_sudo.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'employee':
            grouped_appraisals = [Appraisal_sudo.concat(*g) for k, g in groupbyelem(appraisals, itemgetter('employee_id'))]
        else:
            grouped_appraisals = [appraisals]
        # employee_id = request.env['hr.employee'].sudo().search([('p','=', request.env.user.id)])

        values.update({
            'team_appraisals': appraisals,
            'team_grouped_appraisals': grouped_appraisals,
            'page_name': 'my_team_appraisals',
            'default_url': '/my/team/appraisals',
            # 'employee_id':employee_id.id,
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
        return request.render("hr_portal_appraisal.portal_my_team_appraisal", values)


    @http.route(['/my/team/appraisal/review/<int:appraisal_id>'], type='http', auth="user", website=True)
    def manager_review_employee_assement(self, appraisal_id, access_token=None, **kw):
        if appraisal_id:
            appraisal = request.env['hr.appraisal'].sudo().browse(appraisal_id)
        # values = self._task_get_page_view_values(task_sudo, access_token, **kw)

        # if appraisal:
        #     if appraisal.state not in ['draft','confirm']:
        #         return request.redirect('/my/appraisals')

        emp_id = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        if not appraisal.employee_id.parent_id.id == emp_id.id or appraisal.manager_review:
            raise AccessDenied('You are not manager of this employee')

        values = {
            'page_name' : 'manager_review',
            'appraisal_manager':appraisal,
        }
        return request.render("hr_portal_appraisal.appraisal_manager_review", values)



    def update_manager_review(self, form_data, **kw):
        if form_data['appraisal_id']:
            manager_review_data = {
                        'ques1': form_data['ques1'] or ' ',
                        'ques2': form_data['ques2'] or ' ',
                        'ques3': form_data['ques3'] or ' ',
                        'ques4': form_data['ques4'] or ' ',
                        'overall_performance': form_data['overall_performance'] or ' ',
                        'ques5_comments': form_data['ques5_comments'] or ' ',
                        
                        }
            html_data = """
                  <div  class="row" style="color:#000000">
                    <div class="col-lg-8 offset-lg-2 mb8 pull-left">
                        <h5 class="mb16 mt16 text-center" style="background-color: #2b2554;color: white;padding: 7px;"> Feedback Form (Counselor)</h5>
                        <p style="text-align:justify">
                            Please note that this form should be filled in by the Counselor prior to the Service Line Normalization/ Validation/ Round Table discussion and necessary examples must be provided for a fruitful discussion.
                        </p>
                        <p style="text-align:justify">
                            Feedback and the annual performance rating are to be communicated to the Counselee after the Normalization meeting.
                        </p>
                    </div>
                    <div class="form-group col-lg-8 offset-lg-2 pull-left">
                        <table class="table table-sm table-bordered">
                        <tr>
                            <td style="border: 1px solid #000000;color: black;">
                                <label class="control-label" for="ques1"><strong>1. Areas of Strengths:</strong></label>
                               <p>%(ques1)s</p>                               
                            </td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #000000;color: black;">
                                <label class="control-label" for="ques2"><strong>2. Areas for improvement:</strong></label>
                               <p>%(ques2)s</p>                               
                            </td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #000000;color: black;">
                                <label class="control-label" for="ques3"><strong>3. Counselee can further build upon his/ her strengths by:</strong></label>
                                <p>%(ques3)s</p>                               
                            </td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #000000;color: black;">
                                <label class="control-label" for="ques4"><strong>4. Counselee needs the following training/ coaching:</strong></label>
                                <p>%(ques4)s</p>                               
                            </td>
                        </tr>
                        </table>
                    </div>
                    <div class="form-group col-lg-8 offset-lg-2 pull-left">
                        <div class="form-group">
                            <label class="col-form-label" for="overall_performance"><strong> Overall Performance Rating:(Please tick as applicable)</strong></label><p>%(overall_performance)s</p>
                        </div>
                    </div>
                    <div class="form-group col-lg-8 offset-lg-2 pull-left">
                       <table class="table table-sm table-bordered">
                           <tr>
                                <td style="border: 1px solid #000000;color: black;">
                                    <label class="control-label" for="ques4"><strong>Comments(if Any)</strong></label>
                                    <p>%(ques5_comments)s</p>                             
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>

            """%(manager_review_data)

        if form_data['appraisal_id']:
            app = request.env['hr.appraisal'].sudo().browse(form_data['appraisal_id'])
            app.write({'manager_review':html_data,'manager_review_submit_date':fields.datetime.today(),'state':'done','overall_performance':form_data['overall_performance']})

            return app



    @http.route(['/manager_review/form/submit/'], type='json', auth="user")
    def submit_manager_review(self, form_data, **kw):
        appraisal = self.update_manager_review(form_data, **kw)
        return {'appraisal_id': appraisal,'error': 0,}



    @http.route(['/appraisal/preview/<int:appraisal_id>'], type='http', auth="user", website=True)
    def manager_preview_employee_assement(self, appraisal_id, access_token=None, **kw):
        if appraisal_id:
            appraisal = request.env['hr.appraisal'].sudo().browse(appraisal_id)
        # values = self._task_get_page_view_values(task_sudo, access_token, **kw)

        # if kw.get('type') == manager:
            

        # if appraisal:
        #     if appraisal.state not in ['draft','confirm']:
        #         return request.redirect('/my/appraisals')

        emp_id = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        if not appraisal.employee_id.parent_id.id == emp_id.id and not appraisal.employee_id.id == emp_id.id:
            raise AccessDenied('You are not manager of this employee')

        values = {
            'page_name' : 'assessment_preview',
            'appraisal_preview':appraisal,
            'access_type':kw.get('type'),
        }
        return request.render("hr_portal_appraisal.preview_appraisal", values)

