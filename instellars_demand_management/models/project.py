from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Project(models.Model):
    _inherit = 'project.project'

    demands_count = fields.Integer(compute='_compute_demand_count', string="Demand Count")



    def _compute_demand_count(self):
        for rec in self:
            demand_data = self.env['demands'].search([('project_id', '=', rec.id),('type','=','demand')])
            rec.demands_count = len(demand_data)

    def get_demand_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Demands',
            'view_mode': 'tree,kanban,graph,pivot,calendar,form,activity',
            'res_model': 'demands',
            'domain': [('project_id', '=', self.id),('type','=','demand')],
        }