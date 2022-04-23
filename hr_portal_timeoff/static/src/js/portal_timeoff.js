odoo.define('hr_portal_timeoff.TimeoffPortal', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


publicWidget.registry.TimeoffPortal = publicWidget.Widget.extend({
    selector: '#new_timeoff_form',

    events: {
        "click button#submit_time_off": "submit_new_timeoff_request",
        "change input[name='half_day']": "onchange_halfday",
        "change input[name='request_unit_hours']": "onchange_custom_hour_boolean",
        "change input.has-error": "check_form_validity",
        "change select.has-error": "check_form_validity",
        "change textarea.has-error": "check_form_validity",
        // "click div.flip": "toggle_details",
        // "click div.flip2": "toggle_tech1_block",
        "change select[name='holiday_status_id']": "onchange_holiday_type",
        // "change select[name='status']": "check_duration_days",
        "change input[name='request_from']": "change_portal_params",
        "change input[name='request_to']": "change_portal_params",
        "change select[name='hours_from']": "change_portal_params",
        "change select[name='hours_to']": "change_portal_params",
        "change select[name='request_date_from_period']": "change_portal_params",
        // "change input[name='unit_amount']": "check_time_format",
        // "click #hidden_box_btn":'modal_open',

    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        this.mutex = new concurrency.Mutex();
        // $('body').attr('id', 'eval_form');
        this.onchange_holiday_type();
        this.change_portal_params();
        // $("input[type='radio']").attr('required', '');
    },

    willStart: function() {
        var def1 = this._super();
        // var req_unit; 
        // var def2 = this._rpc({
        //             model: 'hr.leave',
        //             method: 'get_holiday_request_unit',
        //             args: [[],parseInt($("select[name='holiday_status_id']").val())],
        //         }).then(function (result) {
        //           this.req_unit = result;
        //         });
        
        return Promise.all([def1]);
    },

    // get_dayname: function(){
    //    var date = this.$target.find('input[name="date"]').val();
    //    this.$target.find('input[name="day"]').val(moment(date).format('dddd'));

    // },

    onchange_halfday: function(){
       var request_to_block = this.$target.find('div[id="request_to_block"]');
       var period_block = this.$target.find('div[id="period_block"]');
       var halfday = $("input[name='half_day']")[0].checked;
       if(halfday){
            request_to_block.addClass('d-none');
            period_block.removeClass('d-none');
            $("input[name='request_to']").val($("input[name='request_from']").val());
            $("input[name='number_of_days']").val(0.5);
       }else{
            this.change_portal_params();
            request_to_block.removeClass('d-none');
            period_block.addClass('d-none');
       }


    },

    onchange_custom_hour_boolean: function(){
       var request_to_block = this.$target.find('div[id="request_to_block"]');
       var custom_hr_block = this.$target.find('div[id="custom_hr_block"]');
       var custom_hrs = $("input[name='request_unit_hours']")[0].checked;
       if(custom_hrs){
            request_to_block.addClass('d-none');
            custom_hr_block.removeClass('d-none');
            $("input[name='request_to']").val($("input[name='request_from']").val());
       }else{
            request_to_block.removeClass('d-none');
            custom_hr_block.addClass('d-none');
       }


    },


    onchange_holiday_type: function() {
        var self = this
        // var req_unit; 
        Promise.all([self._rpc({
                    model: 'hr.leave',
                    method: 'get_holiday_request_unit',
                    args: [[],parseInt($("select[name='holiday_status_id']").val())],
                }).then(function (result) {
                    $("input[name='request_unit']").val(result);
                    // self.req_unit = result;
                    var halday_boolean_block = $("div[id='half_day_boolean']");
                    var cust_hr_block = $("div[id='custom_hrs_boolean']");
                    if( result == 'day'){
                        halday_boolean_block.addClass('d-none');
                        cust_hr_block.addClass('d-none');

                    }else if (result == 'half_day'){
                        halday_boolean_block.removeClass('d-none');
                        cust_hr_block.addClass('d-none');
                    }else if( result == 'hour'){
                        halday_boolean_block.removeClass('d-none');
                        cust_hr_block.removeClass('d-none');
                    }
                })]);
        
    },

    change_portal_params: function() {
        var self = this;
        var request_date_from_period = $("select[name='request_date_from_period']").val();
        var request_hour_from = $("select[name='hours_from']").val();
        var request_hour_to =  $("select[name='hours_to']").val();
        var request_date_from = $("input[name='request_from']").val();
        var request_date_to = $("input[name='request_to']").val() ;
        var employee_id = parseInt($("input[name='emp_id']").val());
        var request_unit_half =  $("input[name='half_day']")[0].checked;
        var request_unit_hours =  $("input[name='request_unit_hours']")[0].checked;

        // var req_unit; 
        Promise.all([self._rpc({
                    model: 'hr.leave',
                    method: 'onchange_portal_request_params',
                    args: [[],request_date_from_period, request_hour_from, request_hour_to, request_date_from, request_date_to, employee_id,request_unit_half, request_unit_hours],
                }).then(function (result) { 
                    console.log(result);
                    $("input[name='date_from']").val(result['date_from'])
                    $("input[name='date_to']").val(result['date_to'])
                    $("input[name='number_of_days']").val(result['num_of_days'])

                    if (result['holiday_list']){
                    //     for (var k in result['holiday_list']) {}
                    var op = '<div id="holidays_in_range" class="form-group col-lg-12 pull-left">';
                    
                    for (var i = 0; i < result['holiday_list'].length; i++) {
                        op+='<p class="alert alert-success">'+result['holiday_list'][i]['name']+' on '+result['holiday_list'][i]['date']+'';
                        // console.log(result['holiday_list'][i]['name'],result['holiday_list'][i]['date'])
                    }
                    op +='</div>'

                    $("div#holidays_in_range").replaceWith(op);
                    }


                  })]);
        
    },




    get_form_data: function() {
        return {
            'holiday_status_id': parseInt($("select[name='holiday_status_id']").val()),
            'description': $("textarea[name='description']").val(),
            'request_from_date': $("input[name='request_from']").val(),
            'request_to_date': $("input[name='request_to']").val(),
            'employee_id': parseInt($("input[name='emp_id']").val()),
            'request_date_from_period': $("select[name='request_date_from_period']").val(),
            'half_day': $("input[name='half_day']")[0].checked,
            'number_of_days': parseFloat($("input[name='number_of_days']").val()),
            'request_unit_hours': $("input[name='request_unit_hours']")[0].checked,
            'request_hours_from':$("select[name='hours_from']").val(),
            'request_hours_to':$("select[name='hours_to']").val(),
            'date_from': $("input[name='date_from']").val(),
            'date_to': $("input[name='date_to']").val(),
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

    submit_new_timeoff_request: function(event) {
        var self = this;
        var original_link = this.$target.find('input[name="original_link"]').val();
        if (this.check_form_validity()) {
            var form_info = self.get_form_info();
            self._rpc({
                route: '/portal/timeoff/request/',
                params: form_info,
            }).then(function (data) {
                if (data['error']) {
                    $("button#submit").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
                } else {
                    document.location.href = original_link;
                }
            });
        }
    },



    });

return publicWidget.registry.TimeoffPortal;
});