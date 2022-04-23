from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    applicant_id =  fields.Many2one('hr.applicant', 'applicant id')

    def get_partner_values(self, personal_info):
        return {
            'street_present': personal_info['street_present'],
            'street2_present': personal_info['street2_present'],
            'city_present': personal_info['city_present'],
            'zip_present': personal_info['zip_present'],
            'state_id_present': personal_info['state_id_present'],
            'country_id_present': personal_info['country_id_present'],

            'street_permanent': personal_info['street_permanent'],
            'street2_permanent': personal_info['street2_permanent'],
            'city_permanent': personal_info['city_permanent'],
            'zip_permanent': personal_info['zip_permanent'],
            'state_id_permanent': personal_info['state_id_permanent'],
            'country_id_permanent': personal_info['country_id_permanent'],
            # 'parent_id': personal_info['last_working_company'],

            'phone': personal_info['phone'],
            'name': personal_info['name'],
        }

    def get_bank_values(self, personal_info):
        return {
            'acc_number' : personal_info['acc_number'],
            'acc_holder_name': personal_info['account_holder_name'],

        }

    def get_bank_id(self, personal_info):
        bank_info = self.env['res.bank'].sudo().search([('name','=',personal_info['bank_name']),('bank_ifsc_code','=',personal_info['bank_ifsc_code'])])
        if bank_info:
            return bank_info.id
        else:
            new_bank_id = bank_info.create({'name':personal_info['bank_name'],
                'bank_ifsc_code':personal_info['bank_ifsc_code'],
                'bank_branch':personal_info['bank_branch'],
                })
            return new_bank_id.id

                    # 'street_present', 'street2_present', 'city_present', 'zip_present', 'state_present', 'country_present', 
            # 'street_permanent', 'street2_permanent', 'city_permanent', 'zip_permanent', 'state_permanent', 'country_permanent', 

    def get_employee_values(self, personal_info):
        fields_list = [
            'name', 'job_title', 'applicant_id','blood_group','father_name', 'mother_name', 'phone','skype_id',
            'private_email', 'blood_group', 'birthday', 'place_of_birth', 'country_id','esi_number','title',
            'universal_account_number', 'provident_fund', 'identification_id', 'pan_no', 'emergency_contact', 'emergency_phone',
            'employee_degree', 'degree_type', 'division', 'year_of_pass', 'university_name', 'percentage', 'experience_level', 
            'last_working_company', 'last_drawn_salary', 'last_company_department', 'last_company_designation', 'domain',
            'last_working_day', 'start_date_of_career', 'last_company_employeed_code', 'reason_for_leaving',
            'total_years_of_experience', 'relevant_years_of_experience','address_home_id','marital','bank_account_id',
            'spouse_complete_name','relation_with_employee','emergency_contact_city','emergency_contact_state','emergency_contact_country',
        ]
        result = {field: personal_info[field] for field in fields_list}
        for field in ['image_1920', 'aadhar_doc','pan_doc', 'photo_for_id', 'previous_company_salary_slip', 'previous_company_salary_slip2', 'previous_company_salary_slip3','last_company_releiving_letter', 'last_company_experience_letter', 'last_company_offer_letter','certificate_of_fitness']:
            if personal_info.get(field, False):
                result[field] = personal_info.get(field)
        return result

    def update_personal_info(self, personal_info):
        self.ensure_one()

        # Update personal info on the partner
        partner_values = self.get_partner_values(personal_info)


            # for x in bank_info:
            #     if x.name == personal_info['bank_name'] & x.
            
        # if no_name_write:
        #     del partner_values['name']

        # if self.address_home_id:
        #     partner = self.address_home_id
        #     # We shouldn't modify the partner email like this
        #     partner_values.pop('email', None)
        #     self.address_home_id.write(partner_values)
        # else:
        partner_values['active'] = True
        applicant= self.env['hr.applicant'].sudo().search([('id','=',personal_info['applicant_id'])],limit=1)
        partner_values['parent_id'] = applicant.company_id.partner_id.id
        if personal_info['partner_id']:
            partner= self.env['res.partner'].sudo().search([('id','=',personal_info['partner_id'])],limit=1)
            if partner:
                partner.write(partner_values)
        else:
            partner_values['email'] =  personal_info['private_email']
            partner_values['company_type'] = 'person'
            partner = self.env['res.partner'].create(partner_values)
            if partner:
                applicant.write({'partner_id':partner.id})


        if personal_info['existing_bank_account'] == 'yes':
            bank_details = self.get_bank_values(personal_info)
            bank_id = self.get_bank_id(personal_info)
            bank_details['bank_id'] = bank_id
            bank_details['partner_id'] = partner.id
            bank_account = self.env['res.partner.bank'].create(bank_details)

            personal_info['bank_account_id'] = bank_account.id
        else:
            personal_info['bank_account_id'] = None

        personal_info['address_home_id'] = partner.id

        # Update personal info on the employee
    
        vals = self.get_employee_values(personal_info)
        # print('*****************************',vals['name'],'**********************************')
        # print('*****************************',self,'**********************************')

        # existing_bank_account = self.env['res.partner.bank'].search([('acc_number', '=', personal_info['bank_account'])], limit=1)
        # if existing_bank_account:
        #     bank_account = existing_bank_account
        # else:
        # vals['bank_account_id'] = bank_account.id
        # vals['address_home_id'] = partner.id

        # if partner.type != 'private':
        #     partner.type = 'private'

        # if not no_name_write:
        #     vals['name'] = personal_info['name']

        # if personal_info['birthdate'] != '':
        #     vals.update({'birthday': personal_info['birthdate']})
        # if personal_info['spouse_birthdate'] != '':
        #     vals.update({'spouse_birthdate': personal_info['spouse_birthdate']})

        self.write(vals)


    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.partner_name or contact_name:
                employee = self.env['hr.employee'].create({
                    'name': applicant.partner_name or contact_name,
                    'job_id': applicant.job_id.id or False,
                    'job_title': applicant.job_id.name,
                    'address_home_id': address_id,
                    'applicant_id': applicant.id,
                    'department_id': applicant.department_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                            and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                if applicant.job_id:
                    applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                    applicant.job_id.message_post(
                        body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                        subtype="hr_recruitment.mt_job_applicant_hired")
                applicant.message_post_with_view(
                    'hr_recruitment.applicant_hired_template',
                    values={'applicant': applicant},
                    subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id)

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id
        return dict_act_window


class SkillLevel(models.Model):
    _inherit = 'hr.skill.level'

    is_default = fields.Boolean()

class SkillLevel(models.Model):
    _inherit = 'hr.skill'

    not_applicable = fields.Boolean()

class SkillType(models.Model):
    _inherit = 'hr.skill.type'

    @api.model
    def create(self, vals):
        vals['skill_level_ids'] = [(0,0,{
                                        'name':'Unknown',
                                        'is_default':True,
                                        'level_progress':0,
                                        })]
        return super(SkillType, self).create(vals)

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'


    applicant_id =  fields.Many2one('hr.applicant', 'applicant id')


