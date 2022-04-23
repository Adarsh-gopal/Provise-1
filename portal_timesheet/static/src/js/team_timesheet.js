odoo.define('portal_timesheet.TeamTimesheet', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


publicWidget.registry.TeamTimesheetApproval = publicWidget.Widget.extend({
    selector: '#tm_approval_block',

    events: {
        "click button#submit_timesheet_resubmit_reason": "submit_timesheet_resubmit_reason",
        "click button#timesheet_approve": "approve_timesheet",
        // "click button#export_xls": "export_xls",
        "click button#timesheet_resubmit": "resubmit_timesheet",
        "click button#approve_all": "approve_all_timesheets",
        "click button#resubmit_all": "resubmit_all_timesheets",

    },

    init: function(parent, options) {
        this._super(parent);
        this.dp = new concurrency.DropPrevious();
        this.mutex = new concurrency.Mutex();

    },

    willStart: function() {
        var def1 = this._super();        
        return Promise.all([def1]);
    },

    // export_xls: function(){
    //     $("table#tm_by_mnth_team").table2excel({    
    //                 filename: "Your_File_Name.xls"    
    //             }); 
    // },

    approve_timesheet:function(event) {
        var self = this;
        var $el = $(event.target);
        var $row = $el.closest("tr");    // Find the row
        var $text = $row.find("#timesheet_id").text();

        function doIt() {
            self.mutex.exec(function () {
                return self._rpc({
                     route: '/my/team/timesheet/approve/',
                     params: {'timesheet_id':parseInt($text)},
                    // args: [parseInt($text)],
                }).then(function (data) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Success"),
                        message: 'timesheet Approved',
                        sticky: true,
                    });
                    window.location.reload(true);
                });
            });
        }
       Dialog.confirm(this, _t("Are you sure you want to approve this timesheet"), {
            confirm_callback: doIt,
        });
    },

    approve_all_timesheets:function(event) {
        var self = this;
        var $el = $(event.target);
        var $row = $el.closest("tr");    // Find the row
        var $text = $row.find(".approve_all_ids").text();

        function doIt() {
            self.mutex.exec(function () {
                return self._rpc({
                     route: '/my/team/timesheet/approve_all/',
                     params: {'timesheet_ids':$text},
                    // args: [parseInt($text)],
                }).then(function (data) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Success"),
                        message: 'timesheets Approved',
                        sticky: true,
                    });
                    window.location.reload(true);
                });
            });
        }
       Dialog.confirm(this, _t("Are you sure you want to approve this timesheet"), {
            confirm_callback: doIt,
        });
    },

    resubmit_timesheet:function(event) {
        var self = this;
        var $el = $(event.target);
        var $row = $el.closest("tr");    // Find the row
        var $text = $row.find("#timesheet_id").text();

        $('#timesheet_reject_modal').modal("show");
         $("input[name='tm_id']").val($text);

       //  function doIt() {
       //      self.mutex.exec(function () {
       //          return self._rpc({
       //               route: '/my/team/timesheet/resubmit/',
       //               params: {'timesheet_id':parseInt($text)},
       //              // args: [parseInt($text)],
       //          }).then(function (data) {
       //              self.displayNotification({
       //                  type: 'success',
       //                  title: _t("Success"),
       //                  message: 'successfull requested for resubmiting timesheet',
       //                  sticky: true,
       //              });
       //              window.location.reload(true);
       //          });
       //      });
       //  }
       // Dialog.confirm(this, _t("Are you sure you want to get changes in timesheet?"), {
       //      confirm_callback: doIt,
       //  });
    },

    resubmit_all_timesheets:function(event) {
        var self = this;
        var $el = $(event.target);
        var $row = $el.closest("tr");    // Find the row
        var $text = $row.find(".approve_all_ids").text();

        function doIt() {
            self.mutex.exec(function () {
                return self._rpc({
                     route: '/my/team/timesheet/resubmit_all/',
                     params: {'timesheet_ids':$text},
                    // args: [parseInt($text)],
                }).then(function (data) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Success"),
                        message: 'timesheets requested for resubmit',
                        sticky: true,
                    });
                    window.location.reload(true);
                });
            });
        }
       Dialog.confirm(this, _t("Are you sure you want to resubmit all this timesheet?"), {
            confirm_callback: doIt,
        });
    },
    // refuse_timesheet:function(event) {
    //     var self = this;
    //     var $el = $(event.target);
    //     var $row = $el.closest("tr");    // Find the row
    //     var $text = $row.find("#timesheet_id").text();
    //      $('#timesheet_reject_modal').modal("show");
    //      $("input[name='tm_id']").val($text);

    // },
    disableButton: function (button) {
        $(button).attr('disabled', true);
        $(button).children('.fa-lock').removeClass('fa-lock');
        $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');
    },

    submit_timesheet_resubmit_reason: function() {
        var self = this;
        var form_info = {'review':$("textarea[name='resubmit_reason']").val(),'timesheet_id':parseInt($("input[name='tm_id']").val())};
        console.log(form_info)
        this.disableButton($("button#submit_timesheet_resubmit_reason"));
        self._rpc({
            route: '/my/team/timesheet/resubmit/',
            params: form_info,
        }).then(function (data) {
            if (data['error']) {
                $("button#submit_timesheet_resubmit_reason").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
            } else {
                self.displayNotification({
                    type: 'success',
                    title: _t("Success"),
                    message: 'timesheet moved to refused state',
                    sticky: true,
                });
                setInterval(window.location.reload(true), 15000);
            }
        });
    },

    });

return publicWidget.registry.TeamTimesheetApproval;
});