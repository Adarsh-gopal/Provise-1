from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

#child table models inside hr_recruitment
class ReasonForChange(models.Model):
    _name = "hr.change.reason"
    _description = "Reasons to change the job"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the reasons to change must be unique!')
    ]

    name = fields.Text("Reason For Change", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")

class CurrentLocation(models.Model):
    _name = "hr.location"
    _description = "location"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Location name must be unique!')
    ]

    name = fields.Char("Locations", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")

#child table models for experience(min-max)
class ExperienceRange(models.Model):
    _name = "experience.range"
    _description = "Experience (Min-Max)"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Experience range must be unique!')
    ]

    name = fields.Char("Experience Min-Max", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")


#child table models for delivery sites
class DeliverySites(models.Model):
    _name = "delivery.sites"
    _description = "Delivery sites)"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Delivery sites name range must be unique!')
    ]

    name = fields.Char("Delivery Sites", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")


#Reasons for resigning
class ReasonForResign(models.Model):
    _name = "hr.resign.reason"
    _description = "Reasons to Resigning job"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the reasons to change must be unique!')
    ]

    name = fields.Text("Reason For Resigning", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")


#Reasons for candidate rejection
class ReasonForCandidateReject(models.Model):
    _name = "hr.reject.reason"
    _description = "Reasons to rejcting candidate"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the reasons to change must be unique!')
    ]

    name = fields.Char("Reason For candidate rejection", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")

#Reasons interview Rescheduling
class ReasonForCandidateReject(models.Model):
    _name = "reschedule.reason"
    _description = "Reasons to interview Rescheduling"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the reasons to change must be unique!')
    ]

    name = fields.Char("Reason For Re-Scheduling", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")


class EmployeeSatus(models.Model):
    _name = "employee.status"
    _description = "list of employee status"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the employee status must be unique!')
    ]

    name = fields.Char("status", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")


#Reasons for offboarding from current project
class ReasonForOffBoardResign(models.Model):
    _name = "hr.offboarding.reason"
    _description = "Reasons to Resigning job"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the reasons to change must be unique!')
    ]

    name = fields.Text("Reason For Resigning", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")


class CandidateCourse(models.Model):
    _name = "educational.course"
    _description = "list of courses"
    # _sql_constraints = [
    #     ('name_uniq', 'unique (name)', 'The name of the employee status must be unique!')
    # ]

    name = fields.Char("status", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order")