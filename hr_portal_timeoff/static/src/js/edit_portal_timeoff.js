odoo.define('hr_portal_timeoff.edit_my_timeoff', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var Dialog = require('web.Dialog');
var utils = require('web.utils');

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;

var session = require('web.session');



publicWidget.registry.EditMyTimeOffPortal = publicWidget.Widget.extend({
    selector: '#edit_myleave_form',

    events: {
        "click button#update": "update_my_leave",
        "click button#delete": "delete_my_leave",
        "click button#confirm_leave": "confirm_leave",

        "change input": "show_update_button",
        "change select": "show_update_button",
        "change textarea": "show_update_button",


        "change input[name='half_day']": "onchange_halfday",
        "change input[name='request_unit_hours']": "onchange_custom_hour_boolean",
        "change input.has-error": "check_form_validity",
        "change select.has-error": "check_form_validity",
        "change textarea.has-error": "check_form_validity",
        "change select[name='holiday_status_id']": "onchange_holiday_type",
        "change input[name='request_from']": "change_portal_params",
        "change input[name='request_to']": "change_portal_params",
        "change select[name='hours_from']": "change_portal_params",
        "change select[name='hours_to']": "change_portal_params",
        "change select[name='request_date_from_period']": "change_portal_params",

    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        this.mutex = new concurrency.Mutex();
        this.onchange_holiday_type();
        this.onchange_halfday_in_edit_mode();
        this.onchange_custom_hour_boolean_in_edit_mode();
        
    },

    willStart: function() {
        var def1 = this._super();
        
        return Promise.all([def1]);
    },

    onchange_halfday: function(){
       var request_to_block = this.$target.find('div[id="request_to_block"]');
       var period_block = this.$target.find('div[id="period_block"]');
       var halfday = $("input[name='half_day']")[0].checked;
       if(halfday){
            request_to_block.addClass('d-none');
            period_block.removeClass('d-none');
            $("input[name='request_to']").val($("input[name='request_from']").val());
       }else{
            request_to_block.removeClass('d-none');
            period_block.addClass('d-none');
       }


    },
    onchange_halfday_in_edit_mode: function(){
       var request_to_block = $('div[id="request_to_block"]');
       var period_block = $('div[id="period_block"]');
       var halfday = $("input[name='half_day']")[0].checked;
       if(halfday){
            request_to_block.addClass('d-none');
            period_block.removeClass('d-none');
       }else{
            request_to_block.removeClass('d-none');
            period_block.addClass('d-none');
       }


    },

    show_update_button : function() {
       $('button#update').removeClass('d-none');
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
    onchange_custom_hour_boolean_in_edit_mode: function(){
       var request_to_block = $('div[id="request_to_block"]');
       var custom_hr_block = $('div[id="custom_hr_block"]');
       var custom_hrs = $("input[name='request_unit_hours']")[0].checked;
       if(custom_hrs){
            request_to_block.addClass('d-none');
            custom_hr_block.removeClass('d-none');
            
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

                  })]);
        
    },


    delete_my_leave:function() {
        var self = this;
        function doIt() {
            self.mutex.exec(function () {
                return self._rpc({
                    model: 'hr.leave',
                    method: 'unlink',
                    args: [parseInt($("input[name='leave_id']").val())],
                }).then(function () {
                    document.location.pathname = '/my/leaves/';
                });
            });
        }
       Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
            confirm_callback: doIt,
        });
    },

    confirm_leave:function() {
        var self = this;
        function doIt() {
            self.mutex.exec(function () {
                return self._rpc({
                    model: 'hr.leave',
                    method: 'action_confirm',
                    args: [parseInt($("input[name='leave_id']").val())],
                }).then(function () {
                    document.location.pathname = '/my/leaves/'+parseInt($("input[name='leave_id']").val());
                });
            });
        }
       Dialog.confirm(this, _t("Are you sure you want confirm your leave?"), {
            confirm_callback: doIt,
        });
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
            'leave_id':parseInt($("input[name='leave_id']").val()),
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

    update_my_leave: function(event) {
        var self = this;
        // var original_link = this.$target.find('input[name="original_link"]').val();
        if (this.check_form_validity()) {
            var form_info = self.get_form_info();
            console.log(form_info);
            self._rpc({
                route: '/portal/timeoff/update/',
                params: form_info,
            }).then(function (data) {
                if (data['error']) {
                    $("button#update").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
                } else {
                    var write_date =moment.utc(data['write_date']).local().format('DD-MM-YYYY HH:mm:ss');
                    self.displayNotification({
                        type: 'success',
                        title: _t("Success"),
                        message: 'TImeoff Updated On ' + write_date,
                        sticky: true,
                    });
                    
                    $("button#update").parent().append("<div class='alert alert-success alert-dismissable fade show'> Timeoff Updated on " + write_date + "</div>");
                    $('button#update').addClass('d-none');
                }
            });
        }
    },



    });

return publicWidget.registry.EditMyTimeOffPortal;
});