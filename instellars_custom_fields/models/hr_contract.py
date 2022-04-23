from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import date 
from dateutil import relativedelta


class HrContract(models.Model):
    _inherit = "hr.contract"


    total_ctc = fields.Monetary("Total CTC")
    ghp_premium = fields.Float("GHP Premium")