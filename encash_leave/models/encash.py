from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError, AccessError

class HrEmployeePrivate(models.Model):
	_inherit = 'hr.employee'

	leave_encashnemt_date= fields.Date('Leave Encashnemt Date',groups="hr.group_hr_user")
	leave_count = fields.Float('Leave Encashed',groups="hr.group_hr_user")

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    leave_encashnemt = fields.Date(string='Leave Encashnemt Date')
    z_encash = fields.Float(string='Leaves Encashed')

    def action_payslip_done(self):
        res = super(HrPayslip,self).action_payslip_done()
        for l in self:
            if l.final_settlement_information == True:
                # pay = super(HrPayslip,self).action_payslip_done()
                var = 0
                payslip = self.env['hr.payslip'].search([('employee_id','=',l.employee_id.id)])
                rec = self.env['hr.employee'].search([('id','=',l.employee_id.id)])
                for line in rec:
                    for s in payslip:
                        var += s.z_encash
                        line.leave_count = var
                self.env['custom.allocation'].create({
                    'leave_encashnemt':l.z_encash,
                    'leave_encashnemt_date':l.leave_encashnemt,
                    })
        return res

    # def _compute_leaves(self):
    #     for allocation in self:
    #         leave_type = allocation.holiday_status_id.with_context(employee_id=allocation.employee_id.id)
    #         allocation.max_leaves = leave_type.max_leaves
    #         allocation.leaves_taken = leave_type.leaves_taken


    @api.onchange('employee_id')
    def Onchange_leave(self):
        for l in self:
            if l.final_settlement_information == True:
                alloc = self.env['hr.leave.allocation'].search([('employee_id','=',l.employee_id.id),('state','=','validate'),('holiday_status_id.name','=','Earned Leaves')])
                total_allocated = 0.0
                leaves_taken= 0.0
                for recs in alloc:
                    leave_type = recs.holiday_status_id.with_context(employee_id=recs.employee_id.id)
                    total_allocated = total_allocated +leave_type.max_leaves
                    leaves_taken = leaves_taken+leave_type.leaves_taken

                if total_allocated != 0:
                    l.z_encash = (total_allocated / len(alloc)) - leaves_taken
                else:
                    l.z_encash = 0.0


# class HrHolidays(models.Model):
#     _inherit = 'hr.leave.allocation'

#     leave_encashnemt = fields.Float(string='Leave Encashed')
#     leave_encashnemt_date = fields.Date(string='Leave Encashnemt Date')

class Allocation(models.Model):
    _name = 'custom.allocation'
    _description = 'custom allocation'

    leave_encashnemt = fields.Float(string='Leave Encashed')
    leave_encashnemt_date = fields.Date(string='Leave Encashnemt Date')

