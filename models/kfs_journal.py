from odoo import fields, models, api


class KfsJournal(models.Model):
    _inherit = 'kfs.journal'

    source_document = fields.Selection(
        selection_add=[('donation', 'Donation')],
        ondelete={'donation': 'set default'}
    )

    donation_id = fields.Many2one(
        'donations.donation',
        string='Donation',
        help='The donation associated with this journal entry.',
    )

    def _make_vc(self):
        vc = super()._make_vc()
        if self.source_document != 'donation':
            return vc
        return f"{self.donation_id.name}"

    def _make_org_doc_number(self):
        org_doc_number = super()._make_org_doc_number()
        if self.source_document != 'donation':
            return org_doc_number
        return f"Donation {self.donation_id.name}"

    def _make_description(self):
        description = super()._make_description()
        if self.source_document != 'donation':
            return description
        return f"Donation {self.donation_id.name}"

    def _make_explanation(self):
        explanation = super()._make_explanation()
        if self.source_document != 'donation':
            return explanation
        return f"Donation {self.donation_id.name}"

    def _make_principal_user(self):
        principal_user = super()._make_principal_user()
        if self.source_document != 'donation':
            return principal_user
        return self.donation_id.company_id.kfs_principal_user_name

    def _make_balance_type_code(self):
        balance_type_code = super()._make_balance_type_code()
        if self.source_document != 'donation':
            return balance_type_code
        return self.donation_id.company_id.kfs_default_balance_type_code or 'AC'

    def _make_debit_move_lines(self):
        debit_move_lines = super()._make_debit_move_lines()
        if self.source_document == 'donation':
            debit_move_lines = self.donation_id.payment_id.move_id.line_ids.filtered(lambda l: l.debit > 0)
        return debit_move_lines

    def _make_credit_move_lines(self):
        credit_move_lines = super()._make_credit_move_lines()
        if self.source_document == 'donation':
            # Derive credit move lines from the donation record
            credit_move_lines = self.donation_id.move_id.journal_line_ids.filtered(lambda l: l.credit > 0)
        return credit_move_lines

    def _get_source_document(self, document_id):
        record = super()._get_source_document(document_id)
        if record.source_document == 'donation':
            record = self.env['donations.donation'].browse(document_id)
        return record

    def _get_source_document_field_name(self):
        field_name = super()._get_source_document_field_name()
        if self.source_document == 'donation':
            field_name = 'donation_id'
        return field_name

