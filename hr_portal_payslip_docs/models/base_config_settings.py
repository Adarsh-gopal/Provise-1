import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    payslip_report_template = fields.Many2one('ir.actions.report', domain="[('model','=','hr.payslip'),('report_type','=','qweb-pdf')]")
    fndf_payslip_report_template = fields.Many2one('ir.actions.report', domain="[('model','=','hr.payslip'),('report_type','=','qweb-pdf')]")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            payslip_report_template=int(params.get_param('hr_portal_payslip_docs.payslip_report_template')),
            fndf_payslip_report_template=int(params.get_param('hr_portal_payslip_docs.fndf_payslip_report_template')),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("hr_portal_payslip_docs.payslip_report_template", self.payslip_report_template.id)
        self.env['ir.config_parameter'].sudo().set_param("hr_portal_payslip_docs.fndf_payslip_report_template", self.fndf_payslip_report_template.id)