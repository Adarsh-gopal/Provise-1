odoo.define('kanban_stage_change_vallidation.KanbanController', function (require) {
"use strict";

var KanbanController = require('web.KanbanController')
var Context = require('web.Context');
var core = require('web.core');
var Dialog = require('web.Dialog');
var Domain = require('web.Domain');
var view_dialogs = require('web.view_dialogs');
var viewUtils = require('web.viewUtils');

var _t = core._t;
var qweb = core.qweb;



KanbanController.include({
    _onAddRecordToColumn: function (ev) {
        var self = this;
        var record = ev.data.record;
        var column = ev.target;

        console.log(column.data.value);
        console.log(column);

        self._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['activate_vallidation_in_stage']
            }).then(function (res) {
                if(res == 'True'){
                    Dialog.confirm(self, _t("Are you sure you want to move it to the next stage?"), {
                            confirm_callback:  doIt,
                            cancel_callback: refresh,
                        });
                }
                else if(res == 'False'){
                    return doIt();
                }
            });


        function doIt() {
	        self.alive(self.model.moveRecord(record.db_id, column.db_id, self.handle))
	            .then(function (column_db_ids) {
	                return self._resequenceRecords(column.db_id, ev.data.ids)
	                    .then(function () {
	                        _.each(column_db_ids, function (db_id) {
	                            var data = self.model.get(db_id);
	                            self.renderer.updateColumn(db_id, data);
	                        });
	                    });
	            }).guardedCatch(self.reload.bind(self));
        }

        function refresh(){
        	return self.reload();

        }

        // Dialog.confirm(this, _t("Are you sure you want to move it to the next stage?"), {
        //         confirm_callback:  doIt,
        //         cancel_callback: refresh,
        //     });

    },
});


});