# -*- coding: utf-8 -*-

{
    'name': 'HR Portal Payslip Documents Download',
    'version': '13.0.0.3',
    'category': 'Human Resources/Recruitment',
    
    'summary': 'Portal Payslip Download',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'web',
        'portal',
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_payslip.xml',
        'views/res_config_view.xml',
        # 'views/assets.xml',

 
    ],
    # 'qweb': [
    #     "static/src/xml/formselection.xml",
    #     ],
    'installable': True,
    'application': True,
    'auto_install': False
}