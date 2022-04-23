odoo.define('saletimesheet.salepayment', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;


var ShowSalePaymentLineWidget = AbstractField.extend({
    supportedFieldTypes: ['char'],

    isSet: function() {
        return true;
    },


    _render: function() {
        var self = this;
        var info = JSON.parse(this.value);
        if (!info) {
            this.$el.html('');
            return;
        }
        _.each(info.content, function (k, v){
            k.index = v;
            k.posting_amount = field_utils.format.float(k.posting_amount, {digits: k.digits});
            if (k.posting_date){
                k.posting_date = field_utils.format.date(field_utils.parse.date(k.posting_date, {}, {isUTC: true}));
            }
        });
        this.$el.html(QWeb.render('ShowSalePaymentInfo', {
            lines: info.content,
        }));
        _.each(this.$('.js_sale_payment_info'), function (k, v){
            var content = info.content[v];
            var options = {
                content: function () {
                    var $content = $(QWeb.render('SalePaymentPopOver', {
                        // name: content.name,
                        // journal_name: content.journal_name,
                        date: content.posting_date,
                        amount: content.posting_amount,
                        currency: content.currency,
                        position: content.position,
                        invoice_ref: content.invoice_ref,
                        delivery_site : content.delivery_site,
                        service_period : content.service_period
                        
                    }));
                    // $content.filter('.js_unreconcile_payment').on('click', self._onRemoveMoveReconcile.bind(self));
                    // $content.filter('.js_open_payment').on('click', self._onOpenPayment.bind(self));
                    return $content;
                },
                html: true,
                placement: 'left',
                title: 'Payment Information',
                trigger: 'focus',
                delay: { "show": 0, "hide": 100 },
                container: $(k).parent(), // FIXME Ugly, should use the default body container but system & tests to adapt to properly destroy the popover
            };
            $(k).popover(options);
        });
    },

});

field_registry.add('salepayment', ShowSalePaymentLineWidget);

return {
    ShowSalePaymentLineWidget: ShowSalePaymentLineWidget
};
    
});