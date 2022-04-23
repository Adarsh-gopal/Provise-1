{
    'name': 'Leave Encashment',
    'version': '13.0.0.10',
    'summary': '',
    'description': """.
        """,
    'category': 'Human Resources',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'maintainer': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': "https://www.prixgen.com",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account','hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/encash.xml',
        ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
