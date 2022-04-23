odoo.define('onboarding_form', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');


publicWidget.registry.OnboardingForm = publicWidget.Widget.extend({
    selector: '#hr_cs_form',

    events: {
        "click #hr_cs_submit": "submit_salary_package",
        "click button[name='toggle_personal_information']": "toggle_personal_information",
        "click #send_email": "send_offer_to_responsible",
        "change input.bg-danger": "check_form_validity",
        "change input.document": "onchange_document",
        "change input.half_name": "onchange_half_name",
        "change select[name='marital']": "onchange_marital",
        // "change select[name='spouse_fiscal_status']": "onchange_spouse_fiscal_status",
        // "change input[name='disabled_children_bool']": "onchange_disabled_children",
        // "change input[name='other_dependent_people']": "onchange_other_dependent_people",
        "change input[name='experience_level']": "onchange_experience_level",
        "change input[name='existing_bank_account']": "onchange_bank_details",
        "change input[name='existing_pf_number']": "onchange_pf_details",
        "change input[name='present_permanent_same']": "get_present_address",
        'change select[name="emergency_contact_country"]': '_onCountryChange',
        'change select[name="country_id_permanent"]': '_onPermanentCountryChange',
        'change select[name="country_id_present"]': '_onPresentCountryChange',
        "change input[name='identification_id']": '_vallidate_aadhar_num',
        "change input[name='pan_no']": '_vallidate_pan_num',
        "click span.reset": '_reset_input_doc',
        "keypress input[name='tot_exp_years']":'isNumberKey',
        "keypress input[name='relevant_exp_years']": 'isNumberKey',
        // "click a.add_button": 'append_new_lines',
        // "click div.resume-block a.remove_button": 'remove_new_lines',
        'change select[name="skill_type_id"]': '_onSkillTypeChange',
    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        $('body').attr('id', 'onboarding_form');
        
        $("input[name='year_of_pass']").datepicker({ dateFormat: 'yy' });
        $("#hr_contract_salary select").select2({
            minimumResultsForSearch: -1
        });
        $('.multi-select').select2();
        this.onchange_marital();
        // this.onchange_disabled_children();
        this.onchange_experience_level();
        this.onchange_bank_details();
        this.onchange_pf_details();
        // this._vallidate_aadhar_num();
        // this.onchange_spouse_fiscal_status();
        // this.onchange_other_dependent_people();
        this.get_present_address();
   
        if ($("input[name='freeze']").val()) {
            $('input.advantage_input').attr('disabled', 'disabled');
            $('section#hr_cs_personal_information input.advantage_input').removeAttr('disabled');
        }
    },

    willStart: function() {
        var def1 = this._super();
        // this.$counter = 2;

        this.$state = this.$('select[name="emergency_contact_state"]');
        this.$stateOptions = this.$state.filter(':enabled').find('option:not(:first)');
        this._adaptEmergencyAddressForm();

        this.$Permanentstate = this.$('select[name="state_id_permanent"]');
        this.$PermanentstateOptions = this.$Permanentstate.filter(':enabled').find('option:not(:first)');
        this._adaptPermanentAddressForm();

        this.$Presentstate = this.$('select[name="state_id_present"]');
        this.$PresentstateOptions = this.$Presentstate.filter(':enabled').find('option:not(:first)');
        this._adaptPresentAddressForm();
        
        this.$SkillID = this.$('select[name="skill_id"]');
        this.$SkillTypeOptions = this.$SkillID.filter(':enabled').find('option:not(:first)');
        this._adaptskilltypeForm();

        return Promise.all([def1]);
    },
    // append_new_lines: function(){
    //      var fieldHTML = '<div class="row newrow'+ this.$counter +'"><div class="col-md-5">'+
    //                         '<div class="form-group">'+
    //                            ' <label class="col-form-label" for="skill_id_type'+ this.$counter +'">Skill Type<span style="color:red">*</span></label>'+
    //                            ' <select name="skill_id_type'+ this.$counter +'"  class="form-control " data-placeholder="Select a skill type" required="required">'+
    //                                ' <option>Select..</option>'+
    //                                ' <t t-foreach="skill_types" t-as="skill_type">'+
    //                                  ' <option t-att-value="skill_type.id"><t t-esc="skill_type.name"/></option>'+
    //                              ' </t>'+
    //                            ' </select>'+
    //                        ' </div>'+
    //                    ' </div>'+
    //                    ' <div class="col-md-5">'+
    //                        ' <div class="form-group">'+
    //                            ' <label class="col-form-label"   for="skill_id'+ this.$counter +'">Certification<span style="color:red">*</span></label>'+
    //                            ' <select name="skill_id'+ this.$counter +'" class="form-control" data-placeholder="Select a skills" required="required">'+
    //                                ' <option>Select..</option>'+
    //                                ' <t t-foreach="skills" t-as="skill">'+
    //                                  ' <option t-att-value="skill.id" ><t t-esc="skill.name"/></option>'+
    //                              ' </t>'+
    //                            ' </select>'+
    //                        ' </div>'+
    //                    ' </div>'+
        
    //                    // ' <div class="col-md-2" style="padding-top: 38px;"">'+
    //                        ' <a class="remove_button" title="Add field" style="cursor:hand;float:right"><i class="fa fa-minus"></i>Remove line</a>'+
    //                    ' </div>';

    //         $('div.resume-block').append(fieldHTML); //Add field html
    //         this.$counter++;

    // },

    // remove_new_lines: function(e){
    //     e.preventDefault();
    //     e.stopPropagation();
    //     // console.log('.newrow'+this.$counter);
    //     this.$counter--;
    //     this.$('.newrow'+this.$counter).remove();

       

    // },

    isNumberKey:function(evt){
            var charCode = (evt.which) ? evt.which : evt.keyCode
                if (charCode > 31 && (charCode < 48 || charCode > 57))
                    return false;
                return true;
        },

    _reset_input_doc:function(reset){
        console.log(reset);
         console.log(reset.currentTarget.attributes[2].nodeValue);
        if(reset.currentTarget.attributes[2].nodeValue == 'photo_for_id'){
             $('input[name="photo_for_id"]').val('');
             $('img#photo_for_id_img').addClass('d-none');
             $('iframe#photo_for_id_pdf').addClass('d-none');

         }
         
        if(reset.currentTarget.attributes[2].nodeValue == 'previous_company_salary_slip'){
            $('input[name="previous_company_salary_slip"]').val('');
             $('img#previous_company_salary_slip_img').addClass('d-none');
             $('iframe#previous_company_salary_slip_pdf').addClass('d-none');

         }
        if(reset.currentTarget.attributes[2].nodeValue == 'previous_company_salary_slip2'){
            $('input[name="previous_company_salary_slip2"]').val('');
             $('img#previous_company_salary_slip2_img').addClass('d-none');
             $('iframe#previous_company_salary_slip2_pdf').addClass('d-none');

         }
        if(reset.currentTarget.attributes[2].nodeValue == 'previous_company_salary_slip3'){
            $('input[name="previous_company_salary_slip3"]').val('');
             $('img#previous_company_salary_slip3_img').addClass('d-none');
             $('iframe#previous_company_salary_slip3_pdf').addClass('d-none');

         }

        if(reset.currentTarget.attributes[2].nodeValue == 'last_company_releiving_letter'){
            $('input[name="last_company_releiving_letter"]').val('');
             $('img#last_company_releiving_letter_img').addClass('d-none');
             $('iframe#last_company_releiving_letter_pdf').addClass('d-none');
            
         }
        if(reset.currentTarget.attributes[2].nodeValue == 'last_company_experience_letter'){
            $('input[name="last_company_experience_letter"]').val('');
             $('img#last_company_experience_letter_img').addClass('d-none');
             $('iframe#last_company_experience_letter_pdf').addClass('d-none');
            
         }
        if(reset.currentTarget.attributes[2].nodeValue == 'last_company_offer_letter'){
            $('input[name="last_company_offer_letter"]').val('');
             $('img#last_company_offer_letter_img').addClass('d-none');
             $('iframe#last_company_offer_letter_pdf').addClass('d-none');
            
         }
         if(reset.currentTarget.attributes[2].nodeValue == 'image_1920'){
            $('input[name="image_1920"]').val('');
             $('img#image_1920_img').addClass('d-none');
             $('iframe#image_1920_pdf').addClass('d-none');
            
         }
         if(reset.currentTarget.attributes[2].nodeValue == 'certificate_of_fitness'){
            $('input[name="certificate_of_fitness"]').val('');
             $('img#certificate_of_fitness_img').addClass('d-none');
             $('iframe#certificate_of_fitness_pdf').addClass('d-none');
            
         }
         if(reset.currentTarget.attributes[2].nodeValue == 'pan_doc'){
            $('input[name="pan_doc"]').val('');            
         }
         if(reset.currentTarget.attributes[2].nodeValue == 'aadhar_doc'){
            $('input[name="aadhar_doc"]').val('');  
         }
         

    },

    _adaptskilltypeForm: function () {
        var $skilltype = this.$('select[name="skill_type_id"]');
        var skilltypeID = ($skilltype.val() || 0);
        this.$SkillTypeOptions.detach();
        var $displayedSkillType = this.$SkillTypeOptions.filter('[data-skill_type_id=' + skilltypeID + ']');
        var nb = $displayedSkillType.appendTo(this.$SkillID).show().length;
        this.$SkillID.parent().toggle(nb >= 1);
    },
    _adaptEmergencyAddressForm: function () {
        var $country = this.$('select[name="emergency_contact_country"]');
        var countryID = ($country.val() || 0);
        this.$stateOptions.detach();
        var $displayedState = this.$stateOptions.filter('[data-emergency_contact_country=' + countryID + ']');
        var nb = $displayedState.appendTo(this.$state).show().length;
        this.$state.parent().toggle(nb >= 1);
    },
    _adaptPermanentAddressForm: function () {
        var $country = this.$('select[name="country_id_permanent"]');
        var countryID = ($country.val() || 0);
        this.$PermanentstateOptions.detach();
        var $displayedState = this.$PermanentstateOptions.filter('[data-country_id_permanent=' + countryID + ']');
        var nb = $displayedState.appendTo(this.$Permanentstate).show().length;
        this.$Permanentstate.parent().toggle(nb >= 1);
    },

     _adaptPresentAddressForm: function () {
        var $country = this.$('select[name="country_id_present"]');
        var countryID = ($country.val() || 0);
        this.$PresentstateOptions.detach();
        var $displayedState = this.$PresentstateOptions.filter('[data-country_id_present=' + countryID + ']');
        var nb = $displayedState.appendTo(this.$Presentstate).show().length;
        this.$Presentstate.parent().toggle(nb >= 1);
    },

    _onSkillTypeChange: function () {
        this._adaptskilltypeForm();
    },
    _onCountryChange: function () {
        this._adaptEmergencyAddressForm();
    },
    _onPermanentCountryChange: function () {
        this._adaptPermanentAddressForm();
    },
    _onPresentCountryChange: function () {
        this._adaptPresentAddressForm();
    },
    _vallidate_aadhar_num:function(){
        var adharcard = /^\d{12}$/;

        var aadhar_num  = $("input[name='identification_id']").val();
        if(!aadhar_num.match(adharcard)){
            $("input[name='identification_id']").val("");  
            alert('invalid Aadhar No')

        }



    },
    _vallidate_pan_num:function(){
        var pan = $("input[name='pan_no']").val();   
        var regex = /[A-Z]{5}[0-9]{4}[A-Z]{1}$/;    
        if(!regex.test(pan)){      
            $("input[name='pan_no']").val("");    
            alert("invalid PAN no");    
         
        }



    },

    get_personal_documents: function() {
        var document_names = [ 'image_1920','aadhar_doc','pan_doc', 'photo_for_id',
         'previous_company_salary_slip', 'previous_company_salary_slip2', 'previous_company_salary_slip3', 'last_company_releiving_letter', 'last_company_experience_letter', 'last_company_offer_letter','certificate_of_fitness'];
        var document_srcs = {};
        var promises_list = _.map(document_names, function(document_name) {
            var file = $("input[name='" + document_name + "']");
            return new Promise(function(resolve) {
                if (file[0].files[0]) {
                    utils.getDataURLFromFile(file[0].files[0]).then(function (testString) {
                        var regex = new RegExp(",(.{0,})", "g");
                        var img_src = regex.exec(testString)[1];
                        resolve(img_src);
                    });
                } else {
                    resolve(false);
                }
            }).then(function(img_src) {
                document_srcs[document_name] = img_src;
            });
        });

        return Promise.all(promises_list).then(function() {
            var personal_documents = {
                'image_1920': document_srcs.image_1920,
                'aadhar_doc':document_srcs.aadhar_doc,
                'pan_doc':document_srcs.pan_doc, 
                'photo_for_id':document_srcs.photo_for_id, 
                'previous_company_salary_slip':document_srcs.previous_company_salary_slip, 
                'previous_company_salary_slip2':document_srcs.previous_company_salary_slip2, 
                'previous_company_salary_slip3':document_srcs.previous_company_salary_slip3, 
                'last_company_releiving_letter':document_srcs.last_company_releiving_letter, 
                'last_company_experience_letter':document_srcs.last_company_experience_letter,
                'last_company_offer_letter':document_srcs.last_company_offer_letter,
                'certificate_of_fitness':document_srcs.certificate_of_fitness,
              
            };
            return personal_documents;
        });
    },

    get_personal_info: function() {
        return {
            'name': $("input[name='name']").val(),
            'title':  parseInt($("select[name='title']").val()),
            'applicant_id': $("input[name='applicant_id']").val(),
            'partner_id': $("input[name='partner_id']").val(),
            'gender': $("input[name='gender']:checked").val(),
            'father_name': $("input[name='father_name']").val(),
            'mother_name': $("input[name='mother_name']").val(),
            'phone': $("input[name='phone']").val(),
            'private_email': $("input[name='private_email']").val(),
            'blood_group': $("select[name='blood_group']").val(),
            'birthday': $("input[name='birthdate']").val(),
            'place_of_birth': $("input[name='place_of_birth']").val(),
            'country_id': parseInt($("select[name='country_id']").val()),
            'universal_account_number': $("input[name='universal_account_number']").val(),
            'provident_fund': $("input[name='provident_fund']").val(),
            'esi_number': $("input[name='esi_number']").val(),
            'identification_id': $("input[name='identification_id']").val(),
            'pan_no': $("input[name='pan_no']").val(),

            'emergency_contact': $("input[name='emergency_contact']").val(),
            'emergency_phone': $("input[name='emergency_phone']").val(),
            'relation_with_employee': $("input[name='relation_with_employee']").val(),
            'emergency_contact_city': $("input[name='emergency_contact_city']").val(),
            'emergency_contact_state': parseInt($("select[name='emergency_contact_state']").val()),
            'emergency_contact_country': parseInt($("select[name='emergency_contact_country']").val()),
            'skype_id': $("input[name='skype_id']").val(),

            'street_present': $("input[name='street_present']").val(),
            'street2_present': $("input[name='street2_present']").val(),
            'city_present': $("input[name='city_present']").val(),
            'zip_present': $("input[name='zip_present']").val(),
            'state_id_present': parseInt($("select[name='state_id_present']").val()),
            'country_id_present': parseInt($("select[name='country_id_present']").val()),

            'street_permanent': $("input[name='street_permanent']").val(),
            'street2_permanent': $("input[name='street2_permanent']").val(),
            'city_permanent': $("input[name='city_permanent']").val(),
            'zip_permanent': $("input[name='zip_permanent']").val(),
            'state_id_permanent': parseInt($("select[name='state_id_permanent']").val()),
            'country_id_permanent': parseInt($("select[name='country_id_permanent']").val()),

            'employee_degree':  $("select[name='degree']").val(),
            'degree_type':  parseInt($("select[name='degree_type']").val()),
            'division':  parseInt($("select[name='division']").val()),
            'year_of_pass': $("input[name='year_of_pass']").val(),
            'university_name': $("input[name='university_name']").val(),
            'percentage': $("input[name='percentage']").val(),

            'experience_level': $("input[name='experience_level']:checked").val(),
            'domain':  parseInt($("select[name='domain']").val()),
            'last_working_company': $("input[name='last_working_company']").val(),
            'last_drawn_salary': $("input[name='last_drawn_salary']").val(),
            'last_company_department': $("input[name='last_company_department']").val(),
            'last_company_designation': $("input[name='last_company_designation']").val(),
            'last_working_day': $("input[name='last_working_day']").val(),
            'start_date_of_career': $("input[name='start_date_of_career']").val(),
            'last_company_employeed_code': $("input[name='last_company_employeed_code']").val(),
            'reason_for_leaving': $("textarea[name='reason_for_leaving']").val(),
            'total_years_of_experience': parseFloat($("input[name='tot_exp_years']").val()+'.'+$("select[name='tot_exp_months']").val()),
            'relevant_years_of_experience': parseFloat($("input[name='relevant_exp_years']").val()+'.'+$("select[name='relavant_exp_months']").val()),

            'existing_bank_account': $("input[name='existing_bank_account']:checked").val(),
            'account_holder_name': $("input[name='account_holder_name']").val(),
            'bank_name': $("input[name='bank_name']").val(),
            'acc_number': $("input[name='acc_number']").val(),
            'bank_branch': $("input[name='bank_branch']").val(),
            'bank_ifsc_code': $("input[name='bank_ifsc_code']").val(),
            'marital': $("select[name='marital']").val(),
            'spouse_complete_name': $("input[name='spouse_complete_name']").val(),


            'skill_type_id':  parseInt($("select[name='skill_type_id']").val()),
            'skill_id': $("select[name='skill_id']").val(),

           
            // 'disabled': $("input[name='disabled']")[0].checked,
            // 'spouse_fiscal_status': $("select[name='spouse_fiscal_status']").val(),
            // 'spouse_net_revenue': parseFloat($("input[name='spouse_net_revenue']").val()) || 0.0,
            // 'spouse_other_net_revenue': parseFloat($("input[name='spouse_other_net_revenue']").val()) || 0.0,
            // 'disabled_spouse_bool': $("input[name='disabled_spouse_bool']")[0].checked,
            // 'children': parseInt($("input[name='children']").val()) || 0,
            // 'disabled_children_bool': $("input[name='disabled_children_bool']")[0].checked,
            // 'disabled_children_number': parseInt($("input[name='disabled_children_number']").val()) || 0,
            // 'other_dependent_people': $("input[name='other_dependent_people']")[0].checked,
            // 'other_senior_dependent': parseInt($("input[name='other_senior_dependent']").val()) || 0,
            // 'other_disabled_senior_dependent': parseInt($("input[name='other_disabled_senior_dependent']").val()) || 0,
            // 'other_juniors_dependent': parseInt($("input[name='other_juniors_dependent']").val()) || 0,
            // 'other_disabled_juniors_dependent': parseInt($("input[name='other_disabled_juniors_dependent']").val()) || 0,
            // 'identification_id': $("input[name='identification_id']").val(),
            // 'certificate': $("select[name='certificate']").val(),
            // 'study_field': $("input[name='study_field']").val(),
            // 'study_school': $("input[name='study_school']").val(),
            // 'bank_account': $("input[name='bank_account']").val(),
            // 'country_of_birth': parseInt($("select[name='country_of_birth']").val()),
            // 'spouse_birthdate': $("input[name='spouse_birthdate']").val(),
            // 'km_home_work': parseInt($("input[name='km_home_work']").val()),
            // 'spouse_professional_situation': $("select[name='spouse_professional_situation']").val(),
            'job_title': $("input[name='job_title']").val(),
        };
    },

    get_advantages: function() {
        return {
            'personal_info': this.get_personal_info(),
        };
    },




    onchange_half_name: function() {
        var first_name = $("input[name='first_name']").val();
        var last_name = $("input[name='last_name']").val();
        $("input[name='name']").val(first_name + ' ' + last_name);
    },
    onchange_document: function(input) {
        console.log(input);
        if (input.target.files) {
            utils.getDataURLFromFile(input.target.files[0]).then(function (testString) {
                var regex = new RegExp(",(.{0,})", "g");
                var img_src = regex.exec(testString)[1];
                if (img_src.startsWith('JVBERi0')) {
                    $('iframe#' + input.target.name + '_pdf').attr('src', testString);
                    $('img#' + input.target.name + '_img').addClass('d-none');
                    $('iframe#' + input.target.name + '_pdf').removeClass('d-none');
                } else {
                    $('img#' + input.target.name + '_img').attr('src', testString);
                    $('img#' + input.target.name + '_img').removeClass('d-none');
                    $('iframe#' + input.target.name + '_pdf').addClass('d-none');
                }
            });
        }
    },

    check_form_validity: function() {
        var required_empty_input = _.find($("input:required"), function(input) {return input.value === ''; });
        // var required_empty_select = _.find($("select:required"), function(select) {return $(select).val() === ''; });
        // var email = $("input[name='email']").val();
        // var atpos = email.indexOf("@");
        // var dotpos = email.lastIndexOf(".");
        // var invalid_email = atpos<1 || dotpos<atpos+2 || dotpos+2>=email.length;
        if(required_empty_input) {
            $("button#hr_cs_submit").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + _('Some required fields are not filled') + "</div>");
            _.each($("input:required"), function(input) {
                if (input.value === '') {
                    $(input).addClass('bg-danger');
                } else {
                    $(input).removeClass('bg-danger');
                }
            });
            // _.each($("select:required"), function(select) {
            //     if ($(select).val() === '') {
            //         $(select).parent().find('.select2-choice').addClass('bg-danger');
            //     } else {
            //         $(select).parent().find('.select2-choice').removeClass('bg-danger');
            //     }
            // });
            $("section#hr_cs_personal_information")[0].scrollIntoView({block: "end", behavior: "smooth"});
        }
        // if (invalid_email) {
        //     $("input[name='email']").addClass('bg-danger');
        //     $("button#hr_cs_submit").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + _('Not a valid e-mail address') + "</div>");
        //     $("section#hr_cs_personal_information")[0].scrollIntoView({block: "end", behavior: "smooth"});
        // } else {
        //     $("input[name='email']").removeClass('bg-danger');
        // }
        // $(".alert").delay(4000).slideUp(200, function() {
        //     $(this).alert('close');
        // });
        return  !required_empty_input;
    },

    onchange_marital: function(event) {
        var marital = $("select[name='marital']").val();
        var spouse_info_div = $("div[name='spouse_information']");
        $("div[name='spouse_fiscal_status']").addClass('d-none');
        var spouse_professional_situation_div = $("div[name='spouse_professional_situation']");
        if (marital === 'married' || marital === 'cohabitant') {
            spouse_info_div.removeClass('d-none');
            $("input[name='spouse_complete_name']").attr('required', '');
             spouse_professional_situation_div.removeClass('d-none');
        } else {
            spouse_info_div.addClass('d-none');
         
            $("input[name='spouse_complete_name']").removeAttr('required');
            spouse_professional_situation_div.addClass('d-none');
        }
    },

    onchange_spouse_fiscal_status: function(event) {
        var fiscal_status = $("select[name='spouse_fiscal_status']").val();
        var spouse_revenue_info_div = $("div[name='spouse_revenue_information']");
        spouse_revenue_info_div.addClass('d-none');
    },

    onchange_disabled_children: function(event) {
        var disabled_children = $("input[name='disabled_children_bool']")[0].checked;
        var disabled_children_div = $("div[name='disabled_children_info']");
        disabled_children ? disabled_children_div.removeClass('d-none') : disabled_children_div.addClass('d-none');
    },
    onchange_experience_level: function(event) {
        var experience_level = $("input[name='experience_level']:checked").val();
        var experience_level_div = $("div[name='experience_level']");
        if(experience_level == 'experienced'){
            experience_level_div.removeClass('d-none');
            $("input[name='last_working_company']").attr('required', '');
            $("input[name='domain']").attr('required', '');
            $("input[name='last_drawn_salary']").attr('required', '');
            $("input[name='last_company_department']").attr('required', '');
            $("input[name='last_company_designation']").attr('required', '');
            $("input[name='last_working_day']").attr('required', '');
            $("input[name='start_date_of_career']").attr('required', '');
            $("input[name='tot_exp_years']").attr('required', '');
            $("input[name='relevant_exp_years']").attr('required', '');

            }
            else{
                $("input[name='last_working_company']").removeAttr('required');
                $("input[name='domain']").removeAttr('required');
                $("input[name='last_drawn_salary']").removeAttr('required');
                $("input[name='last_company_department']").removeAttr('required');
                $("input[name='last_company_designation']").removeAttr('required');
                $("input[name='last_working_day']").removeAttr('required');
                $("input[name='start_date_of_career']").removeAttr('required');
                $("input[name='tot_exp_years']").removeAttr('required');
                $("input[name='relevant_exp_years']").removeAttr('required');
                experience_level_div.addClass('d-none');
            }
    },
    onchange_bank_details: function(event) {
        var existing_bank_account = $("input[name='existing_bank_account']:checked").val();
        var existing_bank_account_div = $("div[name='existing_bank_account']");
        var new_bank_account_div = $("div[name='new_bank_account']");
            // $("div[name='new_bank_account']").addClass('d-none');
        if(existing_bank_account == 'yes'){
                new_bank_account_div.addClass('d-none');
                existing_bank_account_div.removeClass('d-none');
                $("input[name='account_holder_name']").attr('required', '');
                $("input[name='bank_name']").attr('required', '');
                $("input[name='acc_number']").attr('required', '');
                $("input[name='bank_branch']").attr('required', '');
                $("input[name='bank_ifsc_code']").attr('required', '');
                }
            else if(existing_bank_account == 'no'){
                new_bank_account_div.removeClass('d-none');
                existing_bank_account_div.addClass('d-none');
                $("input[name='account_holder_name']").removeAttr('required');
                $("input[name='bank_name']").removeAttr('required');
                $("input[name='acc_number']").removeAttr('required');
                $("input[name='bank_branch']").removeAttr('required');
                $("input[name='bank_ifsc_code']").removeAttr('required');

            }
    },
    onchange_pf_details: function(event) {
        var existing_pf_number = $("input[name='existing_pf_number']:checked").val();
        var existing_pf_number_div = $("div[name='existing_pf_number']");
        var new_pf_number_div = $("div[name='new_pf_number']");
            // $("div[name='new_bank_account']").addClass('d-none');
        if(existing_pf_number == 'yes'){
                new_pf_number_div.addClass('d-none');
                existing_pf_number_div.removeClass('d-none');
                $("input[name='provident_fund']").attr('required', '');
              
                }
            else if(existing_pf_number == 'no'){
                new_pf_number_div.removeClass('d-none');
                existing_pf_number_div.addClass('d-none');
                $("input[name='provident_fund']").removeAttr('required');
                

            }
    },

    get_present_address: function(event) {
        var present_permanent_same = $("input[name='present_permanent_same']")[0].checked;
        if(present_permanent_same){
            var street = $("input[name='street_present']").val();
            var street2 = $("input[name='street2_present']").val();
            var city = $("input[name='city_present']").val();
            var zip = $("input[name='zip_present']").val();
            var state = $("select[name='state_id_present']").val();
            var country = $("select[name='country_id_present']").val();

            $("input[name='street_permanent']").val(street);
            $("input[name='street2_permanent']").val(street2);
            $("input[name='city_permanent']").val(city);
            $("input[name='zip_permanent']").val(zip);
            $("select[name='state_id_permanent']").val(state);
            $("select[name='country_id_permanent']").val(country);
            
        }
    },


    onchange_other_dependent_people: function(event) {
        var other_dependent_people = $("input[name='other_dependent_people']")[0].checked;
        var other_dependent_people_div = $("div[name='other_dependent_people_info']");
        other_dependent_people ? other_dependent_people_div.removeClass('d-none') : other_dependent_people_div.addClass('d-none');
    },

    get_form_info: function() {
        var self = this;
        return Promise.resolve(self.get_personal_documents()).then(function(personal_documents) {
            var advantages = self.get_advantages();
            _.extend(advantages.personal_info, personal_documents);

            return {
                // 'contract_id': parseInt($("input[name='contract']")[0].id),
                'token': $("input[name='token']").val(),
                'advantages': advantages,
                'applicant_id': parseInt($("input[name='applicant_id']").val()) || false,
                // 'employee_contract_id': parseInt($("input[name='employee_contract_id']").val()) || false,
                'original_link': $("input[name='original_link']").val()
            };
        });
    },

    send_offer_to_responsible: function(event) {
        var self = this;
        if (this.check_form_validity()) {
            self._rpc({
                route: '/salary_package/send_email/',
                params: {
                    'contract_id': parseInt($("input[name='contract']")[0].id),
                    'token': $("input[name='token']").val(),
                    'advantages': self.get_advantages(),
                    'applicant_id': parseInt($("input[name='applicant_id']").val()) || false,
                    'original_link': $("input[name='original_link']").val(),
                    'contract_type': $("input[name='contract_type']").val(),
                    'job_title': $("input[name='job_title']").val(),
                },
            }).then(function (data) {
                document.location.pathname = '/onboarding/thank_you/' + data;
            });
        }
    },

    submit_salary_package: function(event) {
        var self = this;
        if (this.check_form_validity()) {
            self.get_form_info().then(function(form_info) {
                // var spinner_div = $("div[name='loading_block']");
                // spinner_div.css('visibility', 'visible');

                self._rpc({
                    route: '/onboarding/form/submit/',
                    params: form_info,
                }).then(function (data) {
                    if (data['error']) {
                        $("button#hr_cs_submit").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
                    } else {
                        document.location.pathname ='/onboarding/thank_you/'+ data['applicant_id'];
                    }
                });
            })
        }
    },

    //   toggle_personal_information: function() {
    //     $("button[name='toggle_personal_information']").toggleClass('d-none');
    //     $("div[name='personal_info']").toggle(500);
    //     $("div[name='personal_info_withholding_taxes']").toggle(500);
    // },

});

return publicWidget.registry.OnboardingForm;
});
