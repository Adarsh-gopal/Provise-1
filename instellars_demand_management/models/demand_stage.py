from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class DemandStage(models.Model):
    _name = "demand.stage"
    _description = "Demand Stages"
    _rec_name = 'name'
    _order = "sequence, name, id"


    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    is_won = fields.Boolean('Is Won Stage?')
    requirements = fields.Text('Requirements', help="Enter here the internal requirements for this stage (ex: Offer sent to customer). It will appear as a tooltip over the stage's name.")
    fold = fields.Boolean('Folded in Pipeline',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')


