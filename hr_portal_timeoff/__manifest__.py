# -*- coding: utf-8 -*-

{
    'name': 'HR Portal Timeoff',
    'version': '13.0.0.16',
    'category': 'Human Resources/Recruitment',
    
    'summary': 'Portal Time off ',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'web',
        'portal',
        'hr_holidays',
        'hr',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/timeoff_manager_approval.xml',
        'views/edit_timeoff_portal_view.xml',
        'views/timeoff_portal_views.xml',
        'views/team_portal_timeoff.xml',
        'views/assets.xml',
        'views/hr_employee.xml',

 
    ],
    # 'qweb': [
    #     "static/src/xml/formselection.xml",
    #     ],
    'installable': True,
    'application': True,
    'auto_install': False
}