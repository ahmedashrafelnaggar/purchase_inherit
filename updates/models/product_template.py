from odoo import models, fields

class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    # Inherit the name field from product.product
    qty_in_po_uom = fields.Text(related='product_variant_id.qty_in_po_uom', string="Detailed Qty", readonly=True)
    min_price = fields.Float(string='Minimum Price')

