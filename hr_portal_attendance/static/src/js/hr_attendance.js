odoo.define('hr_portal_attendance.hr_attendance', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var session = require('web.session');
// var utils = require('web.utils');
// var field_utils = require('web.field_utils');


publicWidget.registry.attendance = publicWidget.Widget.extend({
    selector: '.o_hr_attendance_kiosk_mode_container',
    events: {
        "click .o_hr_attendance_sign_in_out_icon":"update_attendance",
        "click .o_hr_attendance_button_dismiss":"dismiss_attendence",
    },

    willStart: function () {
        var self = this;
        var userid= parseInt($("input[name='logged_in_user']").val())
        var originallink =  $("input[name='original_link']").val();
        var utimezone = session.user_context['tz'];
        console.log(userid);

        var def = this._rpc({
                model: 'hr.employee',
                method: 'search_read',
                // domain: [['user_id', '=', this.getSession().uid]],
                // fields: ['attendance_state', 'name', 'hours_today'],
                args: [[['user_id', '=', userid]], ['attendance_state', 'name', 'hours_today']],
                // args:[[userid],userid]
            })
            .then(function (res) {
                console.log(res);
                self.employee = res.length && res[0];
            //     if (res.length) {
            //         self.hours_today = field_utils.format.float_time(self.employee.hours_today);
            //     }
            });

        return Promise.all([def, this._super.apply(this, arguments)]);
    },
 
    dismiss_attendence: function() {
        var originallink =  $("input[name='original_link']").val();
        document.location.href = originallink;
    },

    update_attendance: function () {
        var self = this;
        
        console.log(self);
        this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
            })
            .then(function(result) {
                var format_time = 'HH:mm:ss';
                if (result.action.hours_today) {
                    var duration = moment.duration(result.action.hours_today, "hours");
                    var new_hours_today= duration.hours() + ' hours, ' + duration.minutes() + ' minutes';
                }
                if (result.action) {
                    // self.do_action(result.action);
                    if(result.action.attendance.check_out == false){
                        $('h1#emp_name').replaceWith( "<h1 class='mb0'>Welcome "+result.action.attendance.employee_id[1]+ "!</h1>" );
                        $('h4#work_hrs').replaceWith( "" );
                        $('h3#click_chkdin').replaceWith( "<button class='o_hr_attendance_button_dismiss btn btn-primary btn-lg'><span class='text-capitalize'>Ok</span></button>" );
                        $('a.o_hr_attendance_sign_in_out_icon').replaceWith( "" );
                        $('h3#wc_msg').replaceWith( "<div class='alert alert-info h2 mt16' role='status'> Checked in at <b>"+ moment.utc(result.action.attendance.check_in).local().format(format_time)+"</b></div>" );
                    }
                    else{

                        $('h1#emp_name').replaceWith( "<h1 class='mb0'>Goodbye "+result.action.attendance.employee_id[1]+ "!</h1>" );
                        $('h4#work_hrs').replaceWith( "" );
                        $('h3#click_chkdin').replaceWith( "<button class='o_hr_attendance_button_dismiss btn btn-primary btn-lg'><span class='text-capitalize'>Goodbye</span></button>" );
                        $('a.o_hr_attendance_sign_in_out_icon').replaceWith( "" );
                        $('h3#wc_msg').replaceWith( "<div class='alert alert-info h2 mt16' role='status'> Checked out at <b>"+ moment.utc(result.action.attendance.check_out).local().format(format_time)+"</b><br/><b>"+new_hours_today+"</b></div>" );

                    }
                    // document.location.href = originallink;
                } else if (result.warning) {
                    self.do_warn(result.warning);
                }
            });
    },
});
// core.action_registry.add('hr_attendance_my_attendances', MyAttendances);

return publicWidget.registry.attendance;


});
