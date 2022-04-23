odoo.define('instellars_interview_schedule.interview_eval_form', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');

var Dialog = require('web.Dialog');

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


publicWidget.registry.IntEvalForm = publicWidget.Widget.extend({
    selector: '#hr_eval_form',

    events: {
        "click #hr_eval_form_submit": "submit_evaluation_report",
        "change input.bg-danger": "check_form_validity",
        "click div.flip": "toggle_details",
        "click div.flip2": "toggle_tech1_block",
        "change input[name='kanban_state']": "onchange_kanban_state",
        "click #hidden_box_btn":'modal_open',

    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        $('body').attr('id', 'eval_form');
        // $("input[type='radio']").attr('required', '');
    },

    willStart: function() {
        var def1 = this._super();
        
        return Promise.all([def1]);
    },
    modal_open: function(){
        $('#hidden_box').modal('show');

    },
    toggle_details:function() {
       
        $('div.details-block').toggleClass('d-none');
    },
    toggle_tech1_block:function() {
       
        $('div.tech_interview_block').toggleClass('d-none');
    },
    onchange_kanban_state: function(event) {
        var kanban_state = $("input[name='kanban_state']:checked").val();
        var hold_block = $("div[name='hold_block']");
        var reject_reason_block = $("div[name='reject_reason_block']");
        var reschedule_block = $("div[name='reschedule_block']");
        
        if(kanban_state == 'hold'){
                hold_block.removeClass('d-none');
                reject_reason_block.addClass('d-none');
                reschedule_block.addClass('d-none');
                $("textarea[name='hold_reason']").attr('required', '');
                $("textarea[name='reject_reason']").removeAttr('required');
                $("textarea[name='re_schedule_reason']").removeAttr('required');
                }
        else if(kanban_state == 'done'){
                hold_block.addClass('d-none');
                reject_reason_block.addClass('d-none');
                reschedule_block.addClass('d-none');
                $("textarea[name='hold_reason']").removeAttr('required');
                $("textarea[name='reject_reason']").removeAttr('required');
                $("textarea[name='re_schedule_reason']").removeAttr('required');
        }
        else if(kanban_state == 'blocked'){
                hold_block.addClass('d-none');
                reject_reason_block.removeClass('d-none');
                reschedule_block.addClass('d-none');
                $("textarea[name='hold_reason']").removeAttr('required');
                $("textarea[name='reject_reason']").attr('required', '');
                $("textarea[name='re_schedule_reason']").removeAttr('required');
        }
        else if(kanban_state == 're_schedule'){
                hold_block.addClass('d-none');
                reject_reason_block.addClass('d-none');
                reschedule_block.removeClass('d-none');
                $("textarea[name='hold_reason']").removeAttr('required');
                $("textarea[name='reject_reason']").removeAttr('required');
                $("textarea[name='re_schedule_reason']").attr('required', '');
        }
    },

    get_evaluation_data: function() {
        return {
            'applicant_id': $("input[name='applicant_id']").val(),
            'stage_id': $("input[name='stage_id']").val(),
            'ques1_tech1': $("input[name='ques1_tech1']:checked").val() || '',
            'ques1_tech1_cmnt': $("textarea[name='ques1_tech1_cmnt']").val(),
            
            'ques2_tech1': $("input[name='ques2_tech1']:checked").val() || '',
            'ques2_tech1_cmnt': $("textarea[name='ques2_tech1_cmnt']").val(),

            'ques3_tech1': $("input[name='ques3_tech1']:checked").val() || '',
            'ques3_tech1_cmnt': $("textarea[name='ques3_tech1_cmnt']").val(),

            'ques4_tech1': $("input[name='ques4_tech1']:checked").val() || '',
            'ques4_tech1_cmnt': $("textarea[name='ques4_tech1_cmnt']").val(),

            'ques5_tech1': $("input[name='ques5_tech1']:checked").val() || '',
            'ques5_tech1_cmnt': $("textarea[name='ques5_tech1_cmnt']").val(),

            'ques6_tech1': $("input[name='ques6_tech1']:checked").val() || '',
            'ques6_tech1_cmnt': $("textarea[name='ques6_tech1_cmnt']").val(),

            'ques7_tech1': $("input[name='ques7_tech1']:checked").val() || '',
            'ques7_tech1_cmnt': $("textarea[name='ques7_tech1_cmnt']").val(),

            'ques8_tech1': $("input[name='ques8_tech1']:checked").val() || '',
            'ques8_tech1_cmnt': $("textarea[name='ques8_tech1_cmnt']").val(),

            'ques9_tech1': $("input[name='ques9_tech1']:checked").val() || '',
            'ques9_tech1_cmnt': $("textarea[name='ques9_tech1_cmnt']").val(),

            'ques10_tech1': $("input[name='ques10_tech1']:checked").val() || '',
            'ques10_tech1_cmnt': $("textarea[name='ques10_tech1_cmnt']").val(),

            'ques11_tech1': $("input[name='ques11_tech1']:checked").val() || '',
            'ques11_tech1_cmnt': $("textarea[name='ques11_tech1_cmnt']").val(),

            'ques12_tech1': $("input[name='ques12_tech1']:checked").val() || '',
            'ques12_tech1_cmnt': $("textarea[name='ques12_tech1_cmnt']").val(),

            'ques13_tech1': $("input[name='ques13_tech1']:checked").val() || '',
            'ques13_tech1_cmnt': $("textarea[name='ques13_tech1_cmnt']").val(),

            'ques14_tech1': $("input[name='ques14_tech1']:checked").val() || '',
            'ques14_tech1_cmnt': $("textarea[name='ques14_tech1_cmnt']").val(),

            'ques15_tech1': $("input[name='ques15_tech1']:checked").val() || '',
            'ques15_tech1_cmnt': $("textarea[name='ques15_tech1_cmnt']").val(),

            'ques16_tech1': $("input[name='ques16_tech1']:checked").val() || '',
            'ques16_tech1_cmnt': $("textarea[name='ques16_tech1_cmnt']").val(),

            'ques17_tech1': $("input[name='ques17_tech1']:checked").val() || '',
            'ques17_tech1_cmnt': $("textarea[name='ques17_tech1_cmnt']").val(),

            'ques18_tech1': $("input[name='ques18_tech1']:checked").val() || '',
            'ques18_tech1_cmnt': $("textarea[name='ques18_tech1_cmnt']").val(),

            'ques19_tech1': $("input[name='ques19_tech1']:checked").val() || '',
            'ques19_tech1_cmnt': $("textarea[name='ques19_tech1_cmnt']").val(),

            'ques20_tech1': $("input[name='ques20_tech1']:checked").val() || '',
            'ques20_tech1_cmnt': $("textarea[name='ques20_tech1_cmnt']").val(),

            'ques21_tech1': $("input[name='ques21_tech1']:checked").val() || '',
            'ques21_tech1_cmnt': $("textarea[name='ques21_tech1_cmnt']").val(),

            'tech1_overall_cmnt': $("textarea[name='tech1_overall_cmnt']").val(),

            'kanban_state': $("input[name='kanban_state']:checked").val() || '',

            'hold_reason': $("textarea[name='hold_reason']").val(),
            'reject_reason': $("textarea[name='reject_reason']").val(),
            're_schedule_reason': $("textarea[name='re_schedule_reason']").val(),


            
        };
    },

    get_advantages: function() {
        return {
            'personal_info': this.get_evaluation_data(),
        };
    },

    check_form_validity: function() {

        var required_empty_textarea = _.find($("textarea:required"), function(textarea) {return textarea.value === '';  });
        var names = []
        $('input:radio').each(function () {
            var rname = $(this).attr('name');
            if ($.inArray(rname, names) == -1) names.push(rname);
        });
        var required_empty_input = false;
        $.each(names, function (i, name) {
            if ($('input[name="' + name + '"]:checked').length == 0) {
                required_empty_input = true;
            }
        });
        
        // var required_empty_input = _.find($("input:required"), function(input) {return input.checked == ''; });
        // console.log('checking required field',required_empty_input)
        if(required_empty_input || required_empty_textarea) {
            $("button#hr_eval_form_submit").parent().parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + _('Some required fields are not filled') + "</div>");
            _.each($("input:required"), function(input) {
                if (input.value === '') {
                    $(input).addClass('bg-danger');
                } else {
                    $(input).removeClass('bg-danger');
                }
            });
            _.each($("textarea:required"), function(textarea) {
                if (textarea.value === '') {
                   $(textarea).addClass('bg-warning');
                } else {
                     $(textarea).removeClass('bg-warning');
                }
            });
            $("section#hr_eval_information")[0].scrollIntoView({block: "end", behavior: "smooth"});
        }
        return  !required_empty_input && !required_empty_textarea;
    },


    get_form_info: function() {
        var self = this;
        var advantages = self.get_advantages();

        return {
            'advantages': advantages,
            'applicant_id': parseInt($("input[name='applicant_id']").val()) || false,
            'stage_id': parseInt($("input[name='stage_id']").val()) || false,
            'original_link': $("input[name='original_link']").val()
        };
    },


    // send_offer_to_responsible: function(event) {
    //     var self = this;
    //     if (this.check_form_validity()) {
    //         self._rpc({
    //             route: '/salary_package/send_email/',
    //             params: {
    //                 'advantages': self.get_advantages(),
    //                 'applicant_id': parseInt($("input[name='applicant_id']").val()) || false,
    //                 'original_link': $("input[name='original_link']").val(),
    //                 'stage_id': parseInt($("input[name='stage_id']").val()) || false,
    //             },
    //         }).then(function (data) {
    //             document.location.pathname = '/onboarding/thank_you/' + data;
    //         });
    //     }
    // },

    submit_evaluation_report: function(event) {
        var self = this;
        if (this.check_form_validity()) {
             function doIt() {
             var form_info = self.get_form_info();
                self._rpc({
                    route: '/evaluation/form/submit/',
                    params: form_info,
                }).then(function (data) {
                    if (data['error']) {
                        $("button#hr_eval_form_submit").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
                    } else {
                        document.location.pathname ='/evaluation/thank_you/'+ data['applicant_id'];
                    }
                });
            }
            Dialog.confirm(this, _t("Are you sure want to submit?."), {
                confirm_callback: doIt,
            });
        }
    },

});

return publicWidget.registry.IntEvalForm;
});
