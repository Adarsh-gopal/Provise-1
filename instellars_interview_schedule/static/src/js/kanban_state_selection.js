odoo.define('instellars_interview_schedule.state_selection_instellars', function (require) {
"use strict";

var basic_fields = require('web.basic_fields');
var StateSelectionWidget = basic_fields.StateSelectionWidget;
// var field_registry = require('web.field_registry');

var registry = require('web.field_registry');

var core = require('web.core');
var qweb = core.qweb;

var InstellarsStateSelectionWidget = StateSelectionWidget.extend({
    // template: 'FormSelection',
    // events: {
    //     'click .dropdown-item': '_setSelection',
    // },
    // supportedFieldTypes: ['selection'],


    _prepareDropdownValues: function () {
        var self = this;
        var _data = [];
        var current_stage_id = self.recordData.stage_id && self.recordData.stage_id[0];
        var stage_data = {
            id: current_stage_id,
            legend_normal: this.recordData.legend_normal || undefined,
            legend_blocked : this.recordData.legend_blocked || undefined,
            legend_done: this.recordData.legend_done || undefined,
            legend_progress: this.recordData.legend_progress || undefined,
            legend_hold: this.recordData.legend_hold || undefined,
            legend_not_intrested: this.recordData.legend_not_intrested || undefined,
            legend_rescheduled: this.recordData.legend_rescheduled || undefined,
            legend_closed: this.recordData.legend_closed || undefined,
        };
        _.map(this.field.selection || [], function (selection_item) {
            var value = {
                'name': selection_item[0],
                'tooltip': selection_item[1],
            };
            if (selection_item[0] === 'normal') {
                value.state_name = stage_data.legend_normal ? stage_data.legend_normal : selection_item[1];
            }else if (selection_item[0] === 'done') {
                value.state_class = 'o_status_green';
                value.state_name = stage_data.legend_done ? stage_data.legend_done : selection_item[1];
            }else if (selection_item[0] === 'progress') {
                value.state_class = 'o_status_orange';
                value.state_name = stage_data.legend_progress ? stage_data.legend_progress : selection_item[1];
            }else if (selection_item[0] === 'hold') {
                value.state_class = 'o_status_yellow';
                value.state_name = stage_data.legend_hold ? stage_data.legend_hold : selection_item[1];
            }else if (selection_item[0] === 'not_intrested') {
                value.state_class = 'o_status_brown';
                value.state_name = stage_data.legend_not_intrested ? stage_data.legend_not_intrested : selection_item[1];
            }else if (selection_item[0] === 're_schedule') {
                value.state_class = 'o_status_blue';
                value.state_name = stage_data.legend_rescheduled ? stage_data.legend_rescheduled : selection_item[1];
            }else if (selection_item[0] === 'closed') {
                value.state_class = 'o_status_purple';
                value.state_name = stage_data.legend_closed ? stage_data.legend_closed : selection_item[1];
            }else {
                value.state_class = 'o_status_red';
                value.state_name = stage_data.legend_blocked ? stage_data.legend_blocked : selection_item[1];
            }
            _data.push(value);
        });
        return _data;
    },

    /**
     * This widget uses the FormSelection template but needs to customize it a bit.
     *
     * @private
     * @override
     */
    _render: function () {
        var states = this._prepareDropdownValues();
        // Adapt "FormSelection"
        // Like priority, default on the first possible value if no value is given.
        var currentState = _.findWhere(states, {name: this.value}) || states[0];
        this.$('.o_status')
            .removeClass('o_status_red o_status_green o_status_orange o_status_yellow o_status_brown o_status_blue o_status_purple')
            .addClass(currentState.state_class)
            .prop('special_click', true)
            .parent().attr('title', currentState.state_name)
            .attr('aria-label', this.string + ": " + currentState.state_name);

        // Render "FormSelection.Items" and move it into "FormSelection"
        var $items = $(qweb.render('FormSelection.items', {
            states: _.without(states, currentState)
        }));
        var $dropdown = this.$('.dropdown-menu');
        $dropdown.children().remove(); // remove old items
        $items.appendTo($dropdown);

        // Disable edition if the field is readonly
        var isReadonly = this.record.evalModifiers(this.attrs.modifiers).readonly;
        this.$('a[data-toggle=dropdown]').toggleClass('disabled', isReadonly || false);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Intercepts the click on the FormSelection.Item to set the widget value.
     *
     * @private
     * @param {MouseEvent} ev
     */
    _setSelection: function (ev) {
        ev.preventDefault();
        var $item = $(ev.currentTarget);
        var value = String($item.data('value'));
        this._setValue(value);
        if (this.mode === 'edit') {
            this._render();
        }
    },
});

registry.add('state_selection_instellars', InstellarsStateSelectionWidget);
return InstellarsStateSelectionWidget;




});