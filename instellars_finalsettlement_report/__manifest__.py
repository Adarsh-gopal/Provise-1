{
    'name': 'Instellar finalsettlement report Templates',
    'version': '13.0.0.23',
    'description': """This module consists, the customized invoice Templates""",
    'category': 'Localization',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['hr_contract',
        'hr',
        'hr_holidays',
        'hr_work_entry',
        'mail',
        'web'],
    'data': [

        'reports/finalsettlement_report.xml',
        'views/header_footer.xml',  
        'views/payslip.xml',    
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
