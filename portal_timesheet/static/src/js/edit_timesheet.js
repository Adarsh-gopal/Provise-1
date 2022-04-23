odoo.define('portal_timesheet.edit_timesheet', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var Dialog = require('web.Dialog');
var utils = require('web.utils');

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;

var session = require('web.session');



publicWidget.registry.EditTimesheetPortal = publicWidget.Widget.extend({
    selector: '#edit_timsheet_form',

    events: {
        "click button#update": "update_timesheet",
        "click button#delete": "delete_timesheet",
        "change input[name='date']": "get_dayname",
        // "change input.bg-danger": "check_form_validity",
        // "click div.flip": "toggle_details",
        // "click div.input-group-append": "check_duration_days",
        "change input[name='date']": "check_service_period",
        "change input": "show_update_button",
        // "input input[name='unit_amount']": "show_update_button",
        "change.datetimepicker #datetimepicker3":"check_duration_days",
        "change.datetimepicker #datetimepicker3":"show_update_button",
        "change select": "show_update_button",
        "change textarea": "show_update_button",
        "change select[name='status']": "check_duration_days",
        "change input[name='unit_amount']": "check_duration_days",
        "change input[name='unit_amount']": "check_time_format",
        "keypress input[name='unit_amount']": '_onKeypress',
        // "click #hidden_box_btn":'modal_open',

    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        this.mutex = new concurrency.Mutex();
        var d_hrs1 = $('input[name="duration_hrs"]').val();
        // var d_hrs = moment($('input[name="duration_hrs"]').val(), "hh:mm").format("HH:mm");
        var n = new Date(0,0);
        n.setSeconds(+d_hrs1 * 60 * 60);
        var new_tm = (n.toTimeString().slice(0, 8)).split(':');
        if (parseInt(new_tm[2])>=30){
            new_tm[1] = String(parseInt(new_tm[1])+1)
        }
        
        // console.log(new_tm[0]+':'+new_tm[1]);
        $('input[name="unit_amount"]').val(new_tm[0]+':'+new_tm[1]);

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
        // $('#datetimepicker3').on("change.datetimepicker", function(e) {
        //     this.check_duration_days();
        //   });
        
        return Promise.all([def1,prom]);
    },

    // start: function () {
    //     var self=this;
    //     $('#datetimepicker3').on("change.datetimepicker", this, this.check_duration_days);
    //      var defs = [];
    //     defs.push(this._super.apply(this, arguments));
    //     return Promise.all(defs);
    //     },


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

    show_update_button : function() {
       $('button#update').removeClass('d-none');
    },

    get_dayname: function(){
       var date = this.$target.find('input[name="date"]').val();
       this.$target.find('input[name="day"]').val(moment(date).format('dddd'));

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

    check_time_format: function() {
        var dt_format = /^[0-9][0-9]:[0-9][0-9]$/;
        // var adharcard = /^\d{12}$/;

        var unit_amount  = $("input[name='unit_amount']").val();
        if(!unit_amount.match(dt_format)){
            Dialog.alert(this, _t('Duration Hours format Should be HH:mm '), {
                title: _t('Warning'),
            });
            $("input[name='unit_amount']").val("00:00");  
            return;

        }
    },
    check_service_period: function() {
        var date = this.$target.find('input[name="date"]').val();
        var sale_order = this.$target.find('input[name="sale_order"]').val();
        var today_date = this.$target.find('input[name="today_date"]').val();
        var service_period_from = this.$target.find('input[name="service_period_from"]').val();
        var service_period_to = this.$target.find('input[name="service_period_to"]').val();
        if(date < service_period_from || date > service_period_to && sale_order){
            Dialog.alert(this, _t('Select Date Between '+service_period_from+' And '+service_period_to), {
                title: _t('Warning'),
            });
            return this.$target.find('input[name="date"]').val(" ");
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

    delete_timesheet:function() {
        var self = this;
        var task_id = parseInt($("select[name='task_id']").val())
        function doIt() {
            self.mutex.exec(function () {
                return self._rpc({
                    model: 'account.analytic.line',
                    method: 'unlink',
                    args: [parseInt($("input[name='timesheet_id']").val())],
                }).then(function () {
                    document.location.pathname = '/my/task/'+ task_id;
                });
            });
        }
       Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
            confirm_callback: doIt,
        });
    },

    get_form_data: function() {
        return {
            'project_id': parseInt($("select[name='project_id']").val()),
            'timesheet_id': parseInt($("input[name='timesheet_id']").val()),
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

    update_timesheet: function(event) {
        var self = this;
        // var original_link = this.$target.find('input[name="original_link"]').val();
        if (this.check_form_validity()) {
             if(this.check_duration_is_valid()){
            var form_info = self.get_form_info();
            
            self._rpc({
                route: '/portal/timesheet/update/',
                params: form_info,
            }).then(function (data) {
                if (data['error']) {
                    $("button#update").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
                } else {
                    var write_date =moment.utc(data['write_date']).local().format('DD-MM-YYYY HH:mm:ss');
                    self.displayNotification({
                        type: 'success',
                        title: _t("success"),
                        message: 'Timesheet Updated On ' + write_date,
                        sticky: true,
                    });
                    
                    $("button#update").parent().append("<div class='alert alert-success alert-dismissable fade show'> Timesheet Updated on " + write_date + "</div>");
                    $('button#update').addClass('d-none');
                }
            });
        }
    }
    },



    });

return publicWidget.registry.EditTimesheetPortal;
});