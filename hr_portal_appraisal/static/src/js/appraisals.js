odoo.define('hr_portal_appraisal.selfEmpAssessment', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


publicWidget.registry.SelfEmpAssessment = publicWidget.Widget.extend({
    selector: '#self_assessment_form',

    events: {
        "click button#submit_self_assesment": "submit_self_assesment",
        "change input.has-error": "check_form_validity",
        "change select.has-error": "check_form_validity",
        "change textarea.has-error": "check_form_validity",
    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        this.mutex = new concurrency.Mutex();
;
    },

    willStart: function() {
        var def1 = this._super();
        // var req_unit; 
    
        
        return Promise.all([def1]);
    },

    get_form_data: function() {
        return {
            'ques1': $("textarea[name='ques1']").val(),
            'ques2': $("textarea[name='ques2']").val(),
            'ques3': $("textarea[name='ques3']").val(),
            'ques4': $("textarea[name='ques4']").val(),
            'ques5_1': $("textarea[name='ques5_1']").val(),
            'ques5_2': $("textarea[name='ques5_2']").val(),
            'ques5_3': $("textarea[name='ques5_3']").val(),
            'ques5_4': $("textarea[name='ques5_4']").val(),
            'pdp_ques1_1': $("textarea[name='pdp_ques1_1']").val(),
            'pdp_ques1_2': $("textarea[name='pdp_ques1_2']").val(),
            'pdp_ques2': $("textarea[name='pdp_ques2']").val(),
            'pdp_ques3_1': $("textarea[name='pdp_ques3_1']").val(),
            'pdp_ques3_2': $("textarea[name='pdp_ques3_2']").val(),
            'pdp_ques3_3': $("textarea[name='pdp_ques3_3']").val(),  
            'appraisal_id': parseInt($("input[name='appraisal_id']").val()),  
        };
    },

    get_form_info: function() {
        var self = this;
        var form_data = self.get_form_data();
        return {
            'form_data': form_data,
            // 'original_link': $("input[name='original_link']").val()
        };
    },

    check_form_validity: function() {
        var self = this;
        var required_empty_input = _.find($("input:required"), function(input) {return input.value === ''; });
        var required_empty_textarea = _.find($("textarea:required"), function(textarea) {return textarea.value === '';  });
        var required_empty_select = _.find($("select:required"), function(select) {return $(select).val() === ''; });
        if(required_empty_input || required_empty_textarea || required_empty_select) {
            // $("button#submit").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + _('Some required fields are not filled') + "</div>");
                self.displayNotification({
                    type: 'warning',
                    title: _t("warning"),
                    message: 'Some required fields are empty!!',
                    sticky: true,
                });
            _.each($("input:required"), function(input) {
                if (input.value === '') {
                    $(input).addClass('has-error');
                } else {
                    $(input).removeClass('has-error');
                }
            });
            _.each($("textarea:required"), function(textarea) {
                if (textarea.value === '') {
                   $(textarea).addClass('has-error');
                } else {
                     $(textarea).removeClass('has-error');
                }
            });
            _.each($("select:required"), function(select) {
                if ($(select).val() === '') {
                    $(select).addClass('has-error');
                } else {
                    $(select).removeClass('has-error');
                }
            });
        }

        return  !required_empty_input && !required_empty_textarea && !required_empty_select;
    },

    submit_self_assesment: function(event) {
        var self = this;
        var original_link = this.$target.find('input[name="original_link"]').val();
        if (this.check_form_validity()) {
            function doIt() {
                var form_info = self.get_form_info();
                self._rpc({
                    route: '/self_assessment/form/submit/',
                    params: form_info,
                }).then(function (data) {
                    if (data['error']) {
                        $("button#submit_self_assesment").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
                    } else {
                        // self.displayNotification({
                        //     type: 'success',
                        //     title: _t("success"),
                        //     message: 'Assessment Submitted successfully',
                        //     sticky: true,
                        // });
                        document.location.href = '/my/appraisals/?success=True';
                    }
                });
            }
            Dialog.confirm(this, _t("Are you sure? Form once submitted cannot be modified."), {
            confirm_callback: doIt,
        });
        }
    },

    });

return publicWidget.registry.SelfEmpAssessment;
});

odoo.define('hr_portal_appraisal.ManagerReview', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


publicWidget.registry.ManagerReviewPortal = publicWidget.Widget.extend({
    selector: '#manager_review_form',

    events: {
        "click button#send_manager_review": "send_manager_review",
        "change input.has-error": "check_form_validity",
        "change select.has-error": "check_form_validity",
        "change textarea.has-error": "check_form_validity",
    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        this.mutex = new concurrency.Mutex();
;
    },

    willStart: function() {
        var def1 = this._super();
        // var req_unit; 
    
        
        return Promise.all([def1]);
    },

    get_form_data: function() {
        return {
            'ques1': $("textarea[name='ques1']").val(),
            'ques2': $("textarea[name='ques2']").val(),
            'ques3': $("textarea[name='ques3']").val(),
            'ques4': $("textarea[name='ques4']").val(),
            'overall_performance': $("input[name='overall_performance']:checked").val(),
            'ques5_comments': $("textarea[name='ques5_comments']").val(), 
            'appraisal_id': parseInt($("input[name='appraisal_id']").val()),  
        };
    },

    get_form_info: function() {
        var self = this;
        var form_data = self.get_form_data();
        return {
            'form_data': form_data,
            // 'original_link': $("input[name='original_link']").val()
        };
    },

    check_form_validity: function() {
        var self = this;
        var required_empty_input = _.find($("input:required"), function(input) {return input.value === ''; });
        var required_empty_textarea = _.find($("textarea:required"), function(textarea) {return textarea.value === '';  });
        var required_empty_select = _.find($("select:required"), function(select) {return $(select).val() === ''; });
        if(required_empty_input || required_empty_textarea || required_empty_select) {
            // $("button#submit").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + _('Some required fields are not filled') + "</div>");
                self.displayNotification({
                    type: 'warning',
                    title: _t("Warning"),
                    message: 'Some required fields are empty!!',
                    sticky: true,
                });
            _.each($("input:required"), function(input) {
                if (input.value === '') {
                    $(input).addClass('has-error');
                } else {
                    $(input).removeClass('has-error');
                }
            });
            _.each($("textarea:required"), function(textarea) {
                if (textarea.value === '') {
                   $(textarea).addClass('has-error');
                } else {
                     $(textarea).removeClass('has-error');
                }
            });
            _.each($("select:required"), function(select) {
                if ($(select).val() === '') {
                    $(select).addClass('has-error');
                } else {
                    $(select).removeClass('has-error');
                }
            });
        }

        return  !required_empty_input && !required_empty_textarea && !required_empty_select;
    },

    send_manager_review: function(event) {
        var self = this;
        // var original_link = this.$target.find('input[name="original_link"]').val();
        if (this.check_form_validity()) {
            function doIt() {
                var form_info = self.get_form_info();
                self._rpc({
                    route: '/manager_review/form/submit/',
                    params: form_info,
                }).then(function (data) {
                    if (data['error']) {
                        $("button#send_manager_review").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
                    } else {
                        // self.displayNotification({
                        //     type: 'success',
                        //     title: _t("success"),
                        //     message: 'Assessment Submitted successfully',
                        //     sticky: true,
                        // });
                          document.location.href = '/my/team/appraisals/';
                    }
                });
            }
            Dialog.confirm(this, _t("Are you sure? Form once submitted cannot be modified."), {
                confirm_callback: doIt,
            });
        }
    },

    });

return publicWidget.registry.ManagerReview;
});