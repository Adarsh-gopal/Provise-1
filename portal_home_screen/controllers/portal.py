from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter

from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class EmployeePortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(EmployeePortal, self)._prepare_portal_layout_values()
        employee =  request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)], limit=1)
       
        values['employee_data'] = employee
        return values