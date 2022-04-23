# -*- coding: utf-8 -*-

{
    'name': 'HR Portal Appraisal',
    'version': '13.0.0.5',
    'category': 'Human Resources/Recruitment',
    
    'summary': 'Portal Appraisal',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'web',
        'portal',
        'hr_appraisal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/self_appraisal_portal_view.xml',
        'views/self_assessment_page.xml',
        'views/team_appraisal_portal_view.xml',
        'views/manager_review_page.xml',
        'views/hr_appraisal_form_view.xml',
        'views/assets.xml',
        'wizards/raise_appraisal_wiz.xml',
        'views/appraisal_config_setting.xml',

 
    ],
    # 'qweb': [
    #     "static/src/xml/formselection.xml",
    #     ],
    'installable': True,
    'application': True,
    'auto_install': False
}