from odoo import fields, models, api


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_company_shipping = fields.Boolean(string="Company Shipping")
    is_trans_department = fields.Boolean(string="transportation department")