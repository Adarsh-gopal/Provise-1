odoo.define('hr_portal_timeoff.TeamTimeoff', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


publicWidget.registry.TeamTimeoff = publicWidget.Widget.extend({
    selector: '#wrap',

    events: {
        "click button#submit_timeoff_review": "submit_refuse_review",
        "click button#approve": "approve_timeoff",
        "click button#refuse": "refuse_timeoff",
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

    approve_timeoff:function(event) {
        var self = this;
        var $el = $(event.target);
        var $row = $el.closest("tr");    // Find the row
        var $text = $row.find("#leave_id").text();

        function doIt() {
            self.mutex.exec(function () {
                return self._rpc({
                     route: '/my/team/leaves/approve/',
                     params: {'leave_id':parseInt($text)},
                    // args: [parseInt($text)],
                }).then(function (data) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Success"),
                        message: 'Timeoff Approved',
                        sticky: true,
                    });
                    window.location.reload(true);
                });
            });
        }
       Dialog.confirm(this, _t("Are you sure you want to approve this timeoff"), {
            confirm_callback: doIt,
        });
    },
    refuse_timeoff:function(event) {
        var self = this;
        var $el = $(event.target);
        var $row = $el.closest("tr");    // Find the row
        var $text = $row.find("#leave_id").text();
         $('#manager_review_modal').modal("show");
         $("input[name='leave_id']").val($text);

    },
    disableButton: function (button) {
        $(button).attr('disabled', true);
        $(button).children('.fa-lock').removeClass('fa-lock');
        $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');
    },

    submit_refuse_review: function() {
        var self = this;
        var form_info = {'review':$("textarea[name='report_note']").val(),'leave_id':parseInt($("input[name='leave_id']").val())};
        this.disableButton($("button#submit_timeoff_review"));
        self._rpc({
            route: '/my/team/leaves/refuse/',
            params: form_info,
        }).then(function (data) {
            if (data['error']) {
                $("button#submit_timeoff_review").parent().append("<div class='alert alert-danger alert-dismissable fade show'>" + data['error_msg'] + "</div>");
            } else {
                self.displayNotification({
                    type: 'success',
                    title: _t("Success"),
                    message: 'Timeoff moved to refused state',
                    sticky: true,
                });
                setInterval(window.location.reload(true), 15000);
            }
        });
    },

    });

return publicWidget.registry.TeamTimeoff;
});