from odoo import models, fields ,api ,_
from odoo.exceptions import UserError, ValidationError

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    balance_end_real = fields.Monetary('Ending Balance',compute='_compute_ending_balance', recursive=True, readonly=True, store=True,
                                       tracking=True)

    @api.depends('balance_end')
    def _compute_ending_balance(self):
        for statement in self:
            if statement.balance_end :
                statement.balance_end_real = statement.balance_end
            else:
                super(AccountBankStatement, statement)._compute_ending_balance()

    def button_post(self):
        if any(statement.state != 'open' for statement in self):
            raise UserError(_("Only new statements can be posted."))

        for statement in self:
            if not statement.name:
                statement._set_next_sequence()

        self.write({'state': 'posted'})
        lines_of_moves_to_post = self.line_ids.filtered(lambda line: line.move_id.state != 'posted')
        if lines_of_moves_to_post:
            lines_of_moves_to_post.move_id._post(soft=False)

    def button_validate(self):
        if any(statement.state != 'posted' or not statement.all_lines_reconciled for statement in self):
            raise UserError(_('All the account entries lines must be processed in order to validate the statement.'))

        for statement in self:

            # Chatter.
            statement.message_post(body=_('Statement %s confirmed.', statement.name))

            # Bank statement report.
            if statement.journal_id.type == 'bank':
                content, content_type = self.env.ref('account.action_report_account_statement')._render(statement.id)
                self.env['ir.attachment'].create({
                    'name': statement.name and _("Bank Statement %s.pdf", statement.name) or _("Bank Statement.pdf"),
                    'type': 'binary',
                    'raw': content,
                    'res_model': statement._name,
                    'res_id': statement.id
                })

        # self._check_balance_end_real_same_as_computed()
        self.write({'state': 'confirm', 'date_done': fields.Datetime.now()})

