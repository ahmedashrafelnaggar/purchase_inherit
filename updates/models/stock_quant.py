from odoo import models, fields,api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # Relate qty_in_po_uom field to product.product
    qty_in_po_uom = fields.Text(related='product_id.qty_in_po_uom', string="Detailed Qty", readonly=True)
    inventory_diff_quantity = fields.Float(
        'Difference', compute='_compute_inventory_diff_quantity', store=True,
        help="Indicates the gap between the product's theoretical quantity and its counted quantity.",
        readonly=True, digits='Product Unit of Measure')
    qty_in_po_uom_int = fields.Integer(string="Qty in PO UOM (Integer)", compute='_compute_qty_in_po_uom_int')

