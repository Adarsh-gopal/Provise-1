import time
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import babel

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons.actual_payroll.model.browsable_object import BrowsableObject_1, InputLine_1, WorkedDays_1, Payslips_1

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    pay_in_ids = fields.One2many('hr.payslip.inherit','slip_id',string='Payslip Lines - Actual ')

    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            payslip.pay_in_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                payslip.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            lines_1 = [(0, 0, line) for line in payslip._get_payslip_lines_1()]
            payslip.write({'line_ids': lines, 'number': number,'state': 'verify', 'compute_date': fields.Date.today()})
            payslip.write({'pay_in_ids': lines_1, 'number': number})
        return True

    def compute_pay_1(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.pay_in_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines_1 = [(0, 0, line) for line in self._get_payslip_lines_1()]
            payslip.write({'pay_in_ids': lines_1, 'number': number})
        return True

    def compute_pay(self):
        for payslip in self:
            contract = self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id)])
            if contract:
                for line in payslip.line_ids:
                    if line.code == "BASIC":
                        line.actual_amount = contract.wage
                    if line.code == "SA":
                        line.actual_amount = contract.supplementary_allowance
                    if line.code == "DA":
                        line.actual_amount = contract.dearness_allowance_id
                    if line.code == "GROSS":
                        line.actual_amount = contract.wage + contract.supplementary_allowance + contract.dearness_allowance_id

    def _get_payslip_lines_1(self):
        def _sum_salary_rule_category_1(localdict, category, actual_amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category_1(localdict, category.parent_id, actual_amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + actual_amount or actual_amount
            return localdict

        # def _sum_salary_rule_category(localdict, category, actual_amount):
        #     if category.parent_id:
        #         localdict = _sum_salary_rule_category(localdict, category.parent_id, actual_amount)
        #     localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + actual_amount
        #     return localdict

        self.ensure_one()
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject_1(employee.id, {}, self.env),
                'rules': BrowsableObject_1(employee.id, rules_dict, self.env),
                'payslip': Payslips_1(employee.id, self, self.env),
                'worked_days': WorkedDays_1(employee.id, worked_days_dict, self.env),
                'inputs': InputLine_1(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract
            }
        }
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition_1(localdict):
                actual_amount, qty, rate = rule._compute_rule_1(localdict)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = actual_amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category_1(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule.name,
                    'note': rule.note,
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'employee_id': employee.id,
                    'actual_amount': actual_amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                }
        return result.values()

    def get_salary_line_total(self, code):
        self.ensure_one()
        line = self.pay_in_ids.filtered(lambda line: line.code == code)
        if line:
            return line[0].total
        else:
            return 0.0


class HrPayslipInherit(models.Model):
    _name = "hr.payslip.inherit"
    _description = " actual payroll lines"
    _order = 'contract_id, sequence'


    name = fields.Char(required=True, translate=True)
    note = fields.Text(string='Description')
    sequence = fields.Integer(required=True, index=True, default=5,
                              help='Use to arrange calculation sequence')
    code = fields.Char(required=True,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                       "In that case, it is case sensitive.")
    slip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    rate = fields.Float(string='Rate (%)', digits='Payroll Rate', default=100.0)
    actual_amount = fields.Float(digits='Payroll')
    quantity = fields.Float(digits='Payroll', default=1.0)
    total = fields.Float(compute='_compute_total', string='Total', digits='Payroll', store=True)

    amount_select = fields.Selection(related='salary_rule_id.actual_select', readonly=True)
    amount_fix = fields.Float(related='salary_rule_id.actual_fix', readonly=True)
    amount_percentage = fields.Float(related='salary_rule_id.actual_percentage', readonly=True)
    appears_on_payslip = fields.Boolean(related='salary_rule_id.appears_on_payslip', readonly=True)
    category_id = fields.Many2one(related='salary_rule_id.category_id', readonly=True, store=True)
    partner_id = fields.Many2one(related='salary_rule_id.partner_id', readonly=True, store=True)

    date_from = fields.Date(string='From', related="slip_id.date_from", store=True)
    date_to = fields.Date(string='To', related="slip_id.date_to", store=True)
    company_id = fields.Many2one(related='slip_id.company_id')

    @api.depends('quantity', 'actual_amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.actual_amount * line.rate / 100

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'employee_id' not in values or 'contract_id' not in values:
                payslip = self.env['hr.payslip'].browse(values.get('slip_id'))
                values['employee_id'] = values.get('employee_id') or payslip.employee_id.id
                values['contract_id'] = values.get('contract_id') or payslip.contract_id and payslip.contract_id.id
                if not values['contract_id']:
                    raise UserError(_('You must set a contract to create a payslip line.'))
        return super(HrPayslipInherit, self).create(vals_list)

    
