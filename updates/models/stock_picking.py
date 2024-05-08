from odoo import api, fields, models, tools, modules, _
from odoo.exceptions import UserError, ValidationError



class StockPicking(models.Model):
    _inherit = "stock.picking"
