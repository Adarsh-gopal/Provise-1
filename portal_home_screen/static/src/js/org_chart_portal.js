odoo.define('portal_home_screen.portal_org_chart', function (require) {
"use strict";

var concurrency = require('web.concurrency');
var publicWidget = require('web.public.widget');
var session = require('web.session');
var utils = require('web.utils');
var core = require('web.core');
// var field_utils = require('web.field_utils');

var QWeb = core.qweb;
var _t = core._t;

var ajax = require('web.ajax');
var xml_load = ajax.loadXML(
    '/portal_home_screen/static/src/xml/hr_portal_org_chart.xml',
    QWeb
);



publicWidget.registry.org_chart = publicWidget.Widget.extend({
    selector: '#org_chart_portal',
    // events: {
    //     "click .o_hr_org_chart_sign_in_out_icon":"update_org_chart",
    //     "click .o_hr_org_chart_button_dismiss":"dismiss_attendence",
    // },

    willStart: function () {
        this.employee = null;
        this.dm = new concurrency.DropMisordered();
        var self = this;
        this._render()
        return Promise.all([this._super.apply(this, arguments)]);
    },

    // _onEmployeeMoreManager: function(event) {
    //     console.log("************************************")
    //     event.preventDefault();
    //     this.employee = parseInt($(event.currentTarget).data('employee-id'));
    //     this._render();
    // },

    _getOrgData: function () {
        var self = this;
        return this.dm.add(this._rpc({
            route: '/hr/get_org_chart',
            params: {
                employee_id: this.employee,
                context: session.user_context,
            },
        })).then(function (data) {
            return data;
        });
    },
     _render: function () {
        // this.preventDefault();
            // if (!this.recordData.id) {
            //     return this.$el.html(QWeb.render("hr_org_chart.hr_org_chart", {
            //         managers: [],
            //         children: [],
            //     }));
            // }
           if (!this.employee) {
                this.employee = parseInt(this.$el.data('employee_id'));
            }

            var self = this;
            return this._getOrgData().then(function (orgData) {
                if (_.isEmpty(orgData)) {
                    orgData = {
                        managers: [],
                        children: [],
                    }
                }
                orgData.view_employee_id = parseInt(self.$el.data('employee_id'));
                self.$el.html(QWeb.render("portal_home_screen.portal_hr_org_chart", orgData));
               
            });
        },

 
});

return publicWidget.registry.org_chart;


});
