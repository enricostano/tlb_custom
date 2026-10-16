# Copyright 2026 Enrico Stano
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    can_edit_customer_invoice_date = fields.Boolean(
        compute="_compute_can_edit_customer_invoice_date",
    )

    @api.depends_context("uid")
    def _compute_can_edit_customer_invoice_date(self):
        can_edit = self.env.user.has_group(
            "tlb_custom.group_edit_customer_invoice_date"
        )
        for move in self:
            move.can_edit_customer_invoice_date = can_edit
