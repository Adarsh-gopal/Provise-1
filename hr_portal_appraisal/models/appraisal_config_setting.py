import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    appraisal_report_template = fields.Many2one('ir.actions.report', domain="[('model','=','hr.appraisal'),('report_type','=','qweb-pdf')]")
   

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            appraisal_report_template=int(params.get_param('hr_portal_appraisal.appraisal_report_template')),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("hr_portal_appraisal.appraisal_report_template", self.appraisal_report_template.id)