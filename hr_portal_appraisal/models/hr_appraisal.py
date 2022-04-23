from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _,SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval



class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"

    employee_assessment = fields.Html(tracking=True)
    employee_assessment_submit_date = fields.Datetime()
    
    manager_review = fields.Html(tracking=True)
    manager_review_submit_date = fields.Datetime()