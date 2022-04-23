odoo.define('portal_timesheet.timesheet', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
    var time = require('web.time');
    var ajax = require('web.ajax');
var utils = require('web.utils');
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


publicWidget.registry.TimesheetPortal = publicWidget.Widget.extend({
    selector: '#new_timsheet_form',

    events: {
        "click button#submit": "submit_timesheet",
        // "change input[name='date']": "get_dayname",
        // "change input.bg-danger": "check_form_validity",
        // "click div.flip": "toggle_details",
        // "click div.flip2": "toggle_tech1_block",
        "change input[name='date']": "check_service_period",
        "change select[name='status']": "check_duration_days",
        "change.datetimepicker #datetimepicker3": "check_duration_days",
        "change input[name='unit_amount']": "check_time_format",
        "keypress input[name='unit_amount']": '_onKeypress',
        // "click #hidden_box_btn":'modal_open',

    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        // $('body').attr('id', 'eval_form');
        // $("input[type='radio']").attr('required', '');
    },

    willStart: function() {
        var def1 = this._super();
        var prom;
            if (!$.fn.datetimepicker) {
                prom = ajax.loadJS("/web/static/lib/tempusdominus/tempusdominus.js");
            }
        $('#datetimepicker3').datetimepicker({
                    format: 'HH:mm',
                    ignoreReadonly:true,
                });
        // $('input[name="unit_amount"]').val('some new value').trigger('check_duration_days');
        return Promise.all([def1,prom]);
    },

    // get_dayname: function(){
    //    var date = this.$target.find('input[name="date"]').val();
    //    this.$target.find('input[name="day"]').val(moment(date).format('dddd'));

    // },
    _onKeypress: function (event) {
        // if (event.keyCode === $.ui.keyCode.ENTER) {
        //     this._add();
        // }
        var charCode = (event.which) ? event.which : event.keyCode
        if (charCode > 31 && (charCode < 48 || charCode > 57)){
            return false;
        }
        return true;
    },

    timetwodecimal:function(t) {
        var arr = t.split(':');
        var dec = parseInt((arr[1]/6)*10, 10);

        return parseFloat(parseInt(arr[0], 10) + '.' + (dec<10?'0':'') + dec);
    }, 

    check_time_format: function() {
        var dt_format = /^[0-9][0-9]:[0-9][0-9]$/;
        // var adharcard = /^\d{12}$/;

        var unit_amount  = $("input[name='unit_amount']").val();
        if(!unit_amount.match(dt_format)){
            Dialog.alert(this, _t('Duration Hours format Should Be HH:mm '), {
                title: _t('Warning'),
            });
            $("input[name='unit_amount']").val("00:00");  
            return;

        }
    },
    check_duration_days: function() {
        var self = this
        var status = this.$target.find('select[name="status"]').val();
        var duration_days_on_status = this.$target.find('input[name="duration_days_on_status"]').val();
        var unit_amount = parseFloat(this.$target.find('input[name="unit_amount"]').val().replace(':','.'));

        if(duration_days_on_status == 'True'){
            if (status == 'full_day'){
                this.$target.find('input[name="duration_days"]').val(1);
                if(unit_amount < 4){
                    self.displayNotification({
                        type: 'warning',
                        title: _t("Warning"),
                        message: 'Duration Hours  Should Be greater than 4 Hours!!',
                        sticky: false,
                    });
                }
            }
            else if (status == 'half_day'){
                this.$target.find('input[name="duration_days"]').val(0.5);
                if(unit_amount > 4){

                    self.displayNotification({
                        type: 'warning',
                        title: _t("Warning"),
                        message: 'Duration Hours  Should Be less than 4 Hours!!',
                        sticky: false,
                    });
                }
            }
            else if (status == 'absent'){
                this.$target.find('input[name="duration_days"]').val(0);
            }
            else if (status == 'weekend'){
                this.$target.find('input[name="duration_days"]').val(0);
            }
            else if (status == 'public_holiday'){
                this.$target.find('input[name="duration_days"]').val(0);
            }
            else if (status == 'comp_off'){
                this.$target.find('input[name="duration_days"]').val(1);
            }
            else{
                this.$target.find('input[name="duration_days"]').val(0);
            }
        }else{
            if (unit_amount >= 5){
                this.$target.find('input[name="duration_days"]').val(1);
            }
            else if(unit_amount < 5 && unit_amount > 0){
                this.$target.find('input[name="duration_days"]').val(0.5);
            }
            else{
                this.$target.find('input[name="duration_days"]').val(0);
            }

        }
   
    },
    check_service_period: function() {
        var date = this.$target.find('input[name="date"]').val();
        var sale_order = this.$target.find('input[name="sale_order"]').val();
        var today_date = this.$target.find('input[name="today_date"]').val();
        var service_period_from = this.$target.find('input[name="service_period_from"]').val();
        var service_period_to = this.$target.find('input[name="service_period_to"]').val();
        if(date < service_period_from || date > service_period_to && sale_order){
            Dialog.alert(this, _t('Select Date Between '+moment(service_period_from).format('DD-MM-YYYY')+' And '+moment(service_period_to).format('DD-MM-YYYY')), {
                title: _t('Warning'),
            });
            this.$target.find('input[name="date"]').val("");
            this.$target.find('input[name="day"]').val("");
            return;
        }else if( date > today_date){
            Dialog.alert(this, _t('You cannot enter timesheet for future date'), {
                title: _t('Warning'),
            });
            this.$target.find('input[name="date"]').val("");
            this.$target.find('input[name="day"]').val("");
            return;
        }
        else{
            this.$target.find('input[name="day"]').val(moment(date).format('dddd'));
        }
    },

    get_form_data: function() {
        return {
            'project_id': parseInt($("select[name='project_id']").val()),
            'task_id': parseInt($("select[name='task_id']").val()),
            'delivery_site': parseInt($("select[name='delivery_site']").val()),
            'status': $("select[name='status']").val(),
            'date': $("input[name='date']").val(),
            'description': $("textarea[name='description']").val(),
            'unit_amount':this.timetwodecimal($("input[name='unit_amount']").val()),
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

    check_duration_is_valid:function(){
        var self = this
        var status = this.$target.find('select[name="status"]').val();
        var duration_days_on_status = this.$target.find('input[name="duration_days_on_status"]').val();
        var unit_amount = parseFloat(this.$target.find('input[name="unit_amount"]').val().replace(':','.'));
        // var valid_duration = false;

        // if(duration_days_on_status == 'True'){
            if (status == 'full_day' && unit_amount < 4){            
                    // this.valid_duration = false;
                    self.displayNotification({
                        type: 'warning',
                        title: _t("Warning"),
                        message: 'Duration Hours  Should Be greater than 4 Hours!!',
                        sticky: true,
                    });
                    return false
            }
            else if (status == 'half_day' && unit_amount > 4){
               
                    // this.valid_duration = false;

                    self.displayNotification({
                        type: 'warning',
                        title: _t("Warning"),
                        message: 'Duration Hours  Should Be less than 4 Hours!!',
                        sticky: false,
                    });
                    return false;
               
            }
            else{
                    return true;
            }
        // }
        // else{
        //     return true;
        // }
    },

    submit_timesheet: function(event) {
        var self = this;
        var original_link = this.$target.find('input[name="original_link"]').val();
        // console.log(this.check_duration_is_valid(),'*******************')
        if (this.check_form_validity()) {
            if(this.check_duration_is_valid()){
            var form_info = self.get_form_info();
            self._rpc({
                route: '/portal/timesheet/submit/',
                params: form_info,
            }).then(function (data) {
                if (data['error']) {
                    $("button#submit").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
                } else {
                    document.location.href = original_link;
                }
            });
        }
    }
    },



    });


publicWidget.registry.TimesheetPortalSubmitAll = publicWidget.Widget.extend({
    selector: '#tm_sheet_table',
    events: {
        "click button#submitt_all_tm": "submitt_all_tm_for_month",
        "click button#export_tm": "export_tm",

    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        this.mutex = new concurrency.Mutex();
        // $('body').attr('id', 'eval_form');
        // $("input[type='radio']").attr('required', '');
    },

    willStart: function() {
        var def1 = this._super();
    
        return Promise.all([def1]);
    },

    export_tm: function(event){
        var self = this;
        var $el = $(event.target);
        var $row = $el.closest("tr");    // Find the row
        var $text = $row.find(".export_class").text();
        console.log($text);

        $("table."+$text).table2excel({    
                    filename: $text+".xls",
                    preserveColors:true,    
                }); 
    },

    submitt_all_tm_for_month:function(event) {
        var self = this;
        var $el = $(event.target);
        var $row = $el.closest("tr");    // Find the row
        var $text = $row.find(".submit_all_ids_for_month").text();
        console.log($text);

        function doIt() {
            self.mutex.exec(function () {
                return self._rpc({
                     route: '/portal/timesheet/submit_all/',
                     params: {'timesheet_ids':$text},
                    // args: [parseInt($text)],
                }).then(function (data) {
                    if (data['error'] == 0){
                        self.displayNotification({
                            type: 'success',
                            title: _t("Success"),
                            message: 'Timesheets Submitted for Approval.',
                            sticky: true,
                        });
                        window.location.reload(true);
                     }
                     else{
                        self.displayNotification({
                            type: 'warning',
                            title: _t("Warning"),
                            message: 'There are no Timesheets for Submission ',
                            sticky: true,
                        });
                     }
                });
            });
        }
       Dialog.confirm(this, _t("Are you sure you want to submit all timesheets for this month"), {
            confirm_callback: doIt,
        });
    },


   });

return publicWidget.registry.TimesheetPortal;
});