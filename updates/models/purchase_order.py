from odoo import fields, models, api


class PurchaseOrderLines(models.Model):
    _inherit = 'purchase.order.line'

    discount_type = fields.Selection([('percentage', 'Percentage'), ('fixed', 'Fixed')], string='Discount Type',
                                     default='percentage')
    discount = fields.Float(string='Discount', digits='Discount')
    discounted_amount = fields.Monetary(string='Tax Excluded', compute='_compute_discounted_amount', store=True)
    purchase_id = fields.Many2one('purchase.order')
    amount_tax = fields.Monetary(compute='_compute_new_field', store=True)
    after_tax = fields.Float(string='after tax')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Tax Included', store=True)


    @api.depends('price_unit', 'product_uom_qty', 'discount_type', 'discount')
    def _compute_discounted_amount(self):
        for line in self:
            if line.discount > 0.0:
                if line.discount_type == 'percentage':
                    total = line.price_unit * line.product_qty
                    discount_amount = total * (line.discount or 0.0) / 100.0
                    line.discounted_amount = total - discount_amount
                elif line.discount_type == 'fixed':
                    total = line.price_unit * line.product_qty
                    line.discounted_amount = total - (line.discount or 0.0)
            else:
                line.discounted_amount = 0.0

    @api.depends('taxes_id.amount')
    def _compute_new_field(self):
        for line in self:
            # Calculate the value based on the selected taxes
            total_tax_amount = sum(line.taxes_id.mapped('amount'))
            line.amount_tax = total_tax_amount

    @api.onchange('taxes_id')
    def _onchange_taxes(self):
        for line in self:
            line.after_tax = 0.0
            if line.taxes_id:
                line.after_tax = line.discounted_amount * line.amount_tax / 100.0

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            if line.discounted_amount:
                line.price_subtotal = line.after_tax + line.discounted_amount
            else:
                super(PurchaseOrderLines, line)._compute_amount()


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_line_id = fields.Many2one('purchase.order.line')
    # discount_amount = fields.Monetary(related='purchase_line_id.discounted_amount')

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     tracking=True)

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.discounted_amount
                amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_total': sum (line.price_subtotal for line in order.order_line),
            })



