{
    'name': 'Instellars Onboarding Form link generator',
    'category': 'Human Resources',
    'version': '13.0.0.18',
    'summary': 'Genrate  Web link to get data from user and send via Email',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'website',
        'hr_skills',
        'web',
        'hr_recruitment',
        'hr',
        
    ],
    'description': """
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/employee_skills.xml',
        'wizard/generate_simulation_link_views.xml',
        'views/hr_applicant_views.xml',
        'views/hr_contract_salary_templates.xml',
        'views/recruitment_stage.xml',
        'views/res_config_settings_views.xml',
        'data/weblink_mail_data.xml',
    ],

}
