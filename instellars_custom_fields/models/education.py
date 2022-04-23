from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError


class EmployeeDegree(models.Model):
    _name = "hr.employee.degree"
    _description = "Employee Degree"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the Degree of Employee must be unique!')
    ]

    name = fields.Char("Degree Name", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order when displaying a list of degrees.")


class EmployeeDegreeType(models.Model):
    _name = "hr.employee.degree.type"
    _description = "Employee Degree type"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the Degree type of Employee must be unique!')
    ]

    name = fields.Char("Degree Type", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order when displaying a list of degrees types.")


class EmployeeDegreeDivision(models.Model):
    _name = "hr.employee.degree.division"
    _description = "Employee Degree type"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the division of Employee passed must be unique!')
    ]

    name = fields.Char("Division", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order when displaying a list of disvion types.")


class WorkDomain(models.Model):
    _name = "hr.employee.domain"
    _description = "Employee Working Domain"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the division of Employee passed must be unique!')
    ]


    name = fields.Char("Domain Name", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order when displaying a list of working domain.")