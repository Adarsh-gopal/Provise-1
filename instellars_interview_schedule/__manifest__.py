{
    'name': 'Instellars Interview Schedule ',
    'version': '13.0.0.16',
    'category': 'Human Resources/Recruitment',
    
    'summary': 'Custom Fields and Functionalities in calendar module',
    'description': """
        Instellar Interview Schedule
    """,
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com/',
    'depends': [
        'web',
        'base',
        'hr_recruitment',
        'calendar',
        'mail',
    ],
    'data': [
        'wizard/generate_evaluation_form.xml',
        'wizard/kanban_state_reason.xml',
        'data/mail_template.xml',
        'data/hrmail.xml',
        'views/calendar_view.xml',
        'views/evaluation_form_template.xml',
        'views/managerial_evaluation_form.xml',
        'views/assets.xml',
        'views/hr_applicant.xml',
 
    ],
    # 'qweb': [
    #     "static/src/xml/formselection.xml",
    #     ],
    'installable': True,
    'application': True,
    'auto_install': False
}