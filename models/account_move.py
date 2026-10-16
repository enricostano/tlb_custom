# Copyright 2026 Enrico Stano
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


RESTRICTED_CUSTOMER_MOVE_TYPES = ("out_invoice", "out_refund")


class AccountMove(models.Model):
    _inherit = "account.move"

    can_edit_customer_invoice_date = fields.Boolean(
        compute="_compute_can_edit_customer_invoice_date",
    )

    @api.model
    def _user_can_edit_customer_invoice_date(self):
        return self.env.user.has_group(
            "tlb_custom.group_edit_customer_invoice_date"
        )

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)

        if "can_edit_customer_invoice_date" in fields_list:
            values["can_edit_customer_invoice_date"] = (
                self._user_can_edit_customer_invoice_date()
            )

        return values

    @api.depends_context("uid")
    def _compute_can_edit_customer_invoice_date(self):
        can_edit = self._user_can_edit_customer_invoice_date()
        for move in self:
            move.can_edit_customer_invoice_date = can_edit

    def _post(self, soft=True):
        if not self._user_can_edit_customer_invoice_date():
            today = fields.Date.context_today(self)

            invalid_moves = self.filtered(
                lambda move: (
                    move.move_type in RESTRICTED_CUSTOMER_MOVE_TYPES
                    and move.invoice_date
                    and move.invoice_date != today
                )
            )

            if invalid_moves:
                raise UserError(
                    _(
                        "You cannot post a customer invoice or credit note "
                        "with an invoice date different from today."
                    )
                )

        return super()._post(soft=soft)
