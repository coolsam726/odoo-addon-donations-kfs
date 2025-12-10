{
    'name': 'KFS Strathmore Donations Extension',
    'version': '1.0.0',
    'summary': 'Extend KFS integration for Strathmore University to support public donations',
    'description': 'This module extends the KFS Strathmore integration to handle donation payments, creating donation records and linking them to payment transactions.',
    'category': 'Accounting',
    'author': 'Sam Maosa',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'donations',
        'kfs_strathmore'
    ],
    'data': [
        # Views
        "views/donations_donation_views.xml",
        "views/kfs_journal_views.xml",
    ],
    'installable': True,
    'auto_install': False
}
