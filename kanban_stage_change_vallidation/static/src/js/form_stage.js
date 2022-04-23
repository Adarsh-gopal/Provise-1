odoo.define('kanban_stage_change_vallidation.relational_fields', function (require) {
"use strict";

var FieldStatus = require('web.relational_fields').FieldStatus;
var AbstractField = require('web.AbstractField');
var basicFields = require('web.basic_fields');
var concurrency = require('web.concurrency');
var ControlPanelView = require('web.ControlPanelView');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var dialogs = require('web.view_dialogs');
var dom = require('web.dom');
var KanbanRecord = require('web.KanbanRecord');
var KanbanRenderer = require('web.KanbanRenderer');
var ListRenderer = require('web.ListRenderer');
var Pager = require('web.Pager');
var rpc = require('web.rpc');
var Dialog = require('web.Dialog');
var session  = require('web.session');

var _t = core._t;
var _lt = core._lt;
var qweb = core.qweb;



FieldStatus.include({
	_onClickStage: function (e) {
		self =this;

		self._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['activate_vallidation_in_stage']
            }).then(function (res) {
                if(res == 'True'){
                    Dialog.confirm(self, _t("Are you sure you want to move it to the next stage?"), {
					                confirm_callback:  doIt,
					            });
                }
                else if(res == 'False'){
                    return doIt();
                }
            });

		 function doIt() {
            return self._setValue($(e.currentTarget).data("value"));
          }

        
            // Dialog.confirm(this, _t("Are you sure you want to move it to the next stage?"), {
            //     confirm_callback:  doIt,
            // });
        },
});


});