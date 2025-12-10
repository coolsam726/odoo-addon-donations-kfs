from odoo import fields, models, api


class DonationsDonation(models.Model):
    _inherit = 'donations.donation'

    kfs_journal_ids = fields.One2many(
        'kfs.journal',
        'donation_id',
        string='KFS Journals',
        domain=[('state', 'not in', ['reversed', 'cancelled'])],
        help='KFS journal entries associated with this donation.'
    )

    kfs_state = fields.Selection(
        string='KFS State',
        compute='_compute_kfs_state',
        help='The KFS state of the donation based on associated KFS Journals.'
    )

    kfs_journals_count = fields.Integer(
        string='KFS Journals Count',
        compute='_compute_kfs_journals_count',
        help='Number of KFS Journals associated with this donation.'
    )

    can_create_kfs_journal = fields.Boolean(
        string='Can Create KFS Journal',
        compute='_compute_can_create_kfs_journal',
        help='Indicates if a KFS Journal can be created for this donation.'
    )

    @api.depends('kfs_journal_ids.state')
    def _compute_kfs_state(self):
        for donation in self:
            latest_journal = donation.kfs_journal_ids.sorted(key='create_date', reverse=True)[:1]
            donation.kfs_state = latest_journal.state if latest_journal else False

    @api.depends('kfs_journal_ids')
    def _compute_kfs_journals_count(self):
        for donation in self:
            donation.kfs_journals_count = len(donation.kfs_journal_ids)

    @api.depends('state', 'kfs_journal_ids')
    def _compute_can_create_kfs_journal(self):
        for donation in self:
            if donation.state == 'posted':
                existing_journals = donation.kfs_journal_ids.filtered(lambda kfs: kfs.state not in ['reversed', 'cancelled'])
                donation.can_create_kfs_journal = len(existing_journals) == 0
            else:
                donation.can_create_kfs_journal = False

    def button_kfs_journals(self):
        self.ensure_one()
        return {
            'name': 'KFS Journals',
            'type': 'ir.actions.act_window',
            'res_model': 'kfs.journal',
            'view_mode': 'tree,form',
            'domain': [('donation_id', '=', self.id)],
            'context': {'default_donation_id': self.id},
        }

    def _create_kfs_journal(self):
        self.ensure_one()
        kfs_journals = self.env['kfs.journal'].search([('donation_id', '=', self.id), ('state', 'not in', ['reversed', 'cancelled'])])
        if kfs_journals:
            return kfs_journals[0]
        journal_vals = {
            'donation_id': self.id,
            'source_document': 'donation',
            'date': self.create_date,
        }
        kfs_journal = self.env['kfs.journal'].create(journal_vals)
        return kfs_journal

    def action_create_kfs_journal(self):
        return self._create_kfs_journal()

    def _cron_create_kfs_journal(self):
        donations = self.search([('state', '=', 'posted')])
        for donation in donations:
            existing_journals = donation.kfs_journal_ids.filtered(lambda kfs: kfs.state not in ['reversed', 'cancelled'])
            if not existing_journals:
                donation._create_kfs_journal()