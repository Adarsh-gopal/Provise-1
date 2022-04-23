{
    'name': 'Instellar Invoice report Templates',
    'version': '13.0.0.10',
    'description': """This module consists, the customized invoice Templates""",
    'category': 'Localization',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['account','l10n_in','web','base','product','sale',],
    'data': [

        'reports/invoice_report.xml',
        'views/header_footer.xml',      
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
