from odoo.exceptions import ValidationError
from odoo import api, models, _, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    shipping_type = fields.Selection(
        [("company_cars", "Company Car"), ("transportation_companies", "Transportation companies")],
        string="Shipping Type",
    )
    shipping_company = fields.Many2one(
        'res.partner',
        string='Shipping Company',
        domain="[('category_id.is_company_shipping', '=', True)]"
    )
    driver_id = fields.Many2one('res.partner', string='Driver',
                                domain="[('category_id.is_trans_department', '=', True)]")

    car_number = fields.Char(string='Car Number')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('waiting_approve', 'Waiting Approve'),
        ('approved', 'Approved'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    discount = fields.Float(string='Discount', digits='Discount', default=0.0, related='order_line.discount')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)],'waiting_approve': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]", )

    @api.model
    def create(self, vals):
        if vals.get('discount', 0.0) > 0.0:
            vals['state'] = 'waiting_approve'
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        if 'discount' in vals and vals['discount'] > 0.0:
            vals['state'] = 'waiting_approve'
        return super(SaleOrder, self).write(vals)

    @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount > 0.0 :
                self.write({'state': 'waiting_approve'})
    def action_approve_sale_order_discount(self):

        if self.env.user.has_group('sales_team.group_sale_manager'):
                 self.write({'state': 'approved'})
        else:
            raise ValidationError("You are not authorized to approve sale orders.")




    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        if self.env.user.has_group('sales_team.group_sale_manager'):
            for order in self:
                default_source_location_id = order.warehouse_id.lot_stock_id.id

                for line in order.order_line:
                    if line.move_ids:
                        line.move_ids.write({
                            'product_uom_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,

                        })

        return res




class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_type = fields.Selection([('percentage', 'Percentage'), ('fixed', 'Fixed')], string='Discount Type', )
    discount = fields.Float(string='Discount', digits='Discount', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_discounted_amount', string='Subtotal', store=True)
    order_id = fields.Many2one('sale.order')

    @api.constrains('price_unit')
    def _check_price_unit(self):
        for line in self:
            if line.product_id and line.product_id.product_tmpl_id.min_price > line.price_unit:
                raise UserError("Price Unit cannot be less than the minimum price.")

    @api.onchange('discount_type')
    def _compute_discounted_amount(self):
        for line in self:
            if line.discount > 0.0:
                if line.discount_type == 'percentage':
                    super(SaleOrderLine, line)._compute_amount()
                elif line.discount_type == 'fixed':
                    total = line.price_unit * line.product_qty
                    line.price_subtotal = total - (line.discount or 0.0)
                    # line.order_id.state = 'waiting_approve'

            else:
                line.price_subtotal = 0.0
                # line.order_id.state = 'waiting_approve'
