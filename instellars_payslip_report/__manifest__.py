{
    'name': 'Instellar payslip report Templates',
    'version': '13.0.0.20',
    'description': """This module consists, the customized invoice Templates""",
    'category': 'Localization',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'hr_contract',
        'hr_holidays',
        'hr_work_entry',
        'mail',
        'web_dashboard',
        'web',
        'actual_payroll'],
    'data': [

        'reports/payslip_report.xml',
        'views/header_footer.xml',      
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
