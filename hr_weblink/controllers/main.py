# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, models, _

from odoo.addons.sign.controllers.main import Sign
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from odoo.tools.image import image_data_uri

from werkzeug.wsgi import get_current_url



class website_hr_applicant_weblink(http.Controller):

    def _check_token_validity(self, token):
        if token:
            contract = request.env['hr.contract'].sudo().search([
                ('access_token', '=', token),
                ('access_token_end_date', '>=', fields.Date.today()),
                ('access_token_consumed', '=', False),
            ], limit=1)
            return contract
        return request.env['hr.contract']


    @http.route(['/onboarding/form/'], type='http', auth="public", website=True)
    def salary_package(self,  **kw):


        if kw.get('applicant_id'):

            # applicant = request.env['hr.applicant'].sudo().browse(int(kw.get('applicant_id')))
            # if not kw.get('token') or \
            #         not applicant.access_token or \
            #         not consteq(applicant.access_token, kw.get('token')) or \
            #         applicant.access_token_end_date < fields.Date.today():
            #     return request.render(
            #         'website.http_error',
            #         {'status_code': 'Oops',
            #          'status_message': 'This link is invalid. Please contact the HR Responsible to get a new one...'})
            existing_emp = request.env['hr.employee'].sudo().search([('applicant_id','=',int(kw.get('applicant_id')))])
  
            if existing_emp.applicant_id.id == int(kw.get('applicant_id')):
                return request.render("hr_weblink.applicant_exist")

        if not kw.get('applicant_id'):
            return request.render(
                'website.http_error',
                {'status_code': 'Oops',
                 'status_message': 'The employee is not linked to an existing user, please contact the administrator..'})

        values = self.get_dropdown_fields()

        redirect_to_job = False
        applicant_id = False       
        job_title = False
        freeze = False
        appl = request.env['hr.applicant'].sudo().search([('id','=',int(kw.get('applicant_id')))])

        for field_name, value in kw.items():
            if field_name == 'job_id':
                redirect_to_job = value
            elif field_name == 'applicant_id':
                applicant_id = value
            elif field_name == 'job_title':
                job_title = value
            else:
                old_value = ""

        values.update({
            'need_personal_information': not redirect_to_job,
            'submit': not redirect_to_job,
            'simulation': False,
            'redirect_to_job': redirect_to_job,
            'applicant_id': applicant_id,
            'current_company':appl.current_company_of_applicant.name,
            'partner_id': appl.partner_id.id,
            'job_title': job_title,
            'freeze': freeze,
            'default_mobile': request.env['ir.default'].sudo().get('hr.applicant', 'mobile'),
            'original_link': get_current_url(request.httprequest.environ)})

        
        return request.render("hr_weblink.weblink_page", values)
        # response.flatten()
        # return response

    def _get_documents_src(self, employee):
        res = {}
        for field in ['id_card', 'image_1920', 'driving_license', 'mobile_invoice', 'sim_card', 'internet_invoice']:
            if employee[field]:
                if employee[field][:7] == b'JVBERi0':
                    img_src = "data:application/pdf;base64,%s" % (employee[field].decode())
                else:
                    img_src = image_data_uri(employee[field])
                res[field] = img_src
            else:
                res[field] = False
        return res


    @http.route(['/onboarding/thank_you/<int:applicant_id>'], type='http', auth="public", website=True)
    def salary_package_thank_you(self, applicant_id=None, **kw):
        applicant = request.env['hr.applicant'].sudo().browse(applicant_id)
        
        return request.render("hr_weblink.salary_package_thank_you", {
            'responsible_name': applicant.user_id.name,
            'responsible_email': applicant.user_id.email,
            'responsible_phone': applicant.user_id.phone,})
        
    def get_dropdown_fields(self):
        return {
            'states': request.env['res.country.state'].sudo().search([]),
            'countries': request.env['res.country'].sudo().search([]),
            'degrees': request.env['hr.employee.degree'].sudo().search([]),
            'degree_type': request.env['hr.employee.degree.type'].sudo().search([]),
            'division': request.env['hr.employee.degree.division'].sudo().search([]),
            'skill_types': request.env['hr.skill.type'].sudo().search([]),
            'skills': request.env['hr.skill'].sudo().search([]),
            'domains': request.env['hr.employee.domain'].sudo().search([]),
            'companies':request.env['res.partner'].sudo().search([('is_company','=','True')]),
            'banks':request.env['res.bank'].sudo().search([]),
            'title':request.env['res.partner.title'].sudo().search([]),

        }


    def create_new_employee(self,  advantages, no_write=False, **kw):
        # Generate a new contract with the current modifications
        personal_info = advantages['personal_info']

        if kw.get('applicant_id'):
            applicant= request.env['hr.applicant'].sudo().browse(kw.get('applicant_id'))
            employee = request.env['hr.employee'].sudo().create({
                'name': 'Onboarding Employee From Link',
                'active': True,
                'company_id': applicant.company_id.id,
            })
            applicant.write({'emp_id':employee.id})


        if personal_info:
            employee.with_context(lang=None).update_personal_info(personal_info)
            if employee:
                mail_template = request.env.ref('hr_weblink.hr_notification_on_onboard')
                mail_template.sudo().send_mail(employee.id, force_send=True)
                level = request.env['hr.skill.level'].sudo().search([('skill_type_id','=',personal_info['skill_type_id']),('is_default','=',True)],limit=1)
                if personal_info['skill_id']:
                    for each in personal_info['skill_id']:
                        request.env['hr.employee.skill'].sudo().create({
                            'employee_id':employee.id,
                            'skill_type_id':personal_info['skill_type_id'],
                            'skill_id':int(each),
                            'skill_level_id':level.id,
                            })
                else:
                    skill_id = request.env['hr.skill'].sudo().search([('skill_type_id','=',personal_info['skill_type_id']),('not_applicable','=',True)],limit=1)
                    request.env['hr.employee.skill'].sudo().create({
                            'employee_id':employee.id,
                            'skill_type_id':personal_info['skill_type_id'],
                            'skill_id':skill_id.id,
                            'skill_level_id':level.id,
                            })

        

        return employee

    

    @http.route(['/onboarding/form/submit/'], type='json', auth='public')
    def submit(self, contract_id=None, token=None, advantages=None, **kw):
        # if kw.get('applicant_id', False):
        #     applicant = request.env['hr.applicant'].sudo().browse(kw.get('applicant_id'))

        new_employee = self.create_new_employee(advantages, no_write=True, **kw)
       

        if new_employee:
            if kw.get('applicant_id'):
                new_employee.sudo().applicant_id = kw.get('applicant_id')

        return {'job_id': new_employee.job_id.id, 'applicant_id':kw.get('applicant_id') }
