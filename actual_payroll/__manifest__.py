
{
    'name': "Actual Payable Amount",
    'version': "13.0.0.4",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'category': "Payroll Summary",
    'data': [
        'security/ir.model.access.csv',
       'views/pay_roll.xml',
       'views/pay_rule.xml',
       'views/pay_slip.xml',
        ],
    'demo': [],
    'depends': ['hr','hr_payroll','hr_contract','l10n_in_hr_payroll'],
    
    'installable': True,
    'application': False,

}
