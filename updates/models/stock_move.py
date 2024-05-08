
from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_id = fields.Many2one('product.product')
    qty_product_available = fields.Float(related='product_id.qty_available',store=True)
    qty_in_po_uom = fields.Text(related='product_id.qty_in_po_uom', string="Detailed Qty", readonly=True)