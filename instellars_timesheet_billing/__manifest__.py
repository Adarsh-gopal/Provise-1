{
    'name': 'instellars billing on timesheet',
    'version': '13.0.0.6',
    'category': 'Human Resources',
    'summary': 'instellars billing customizations',
    'description': 'Instellars billing customizations',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'maintainer': 'Prixgen Tech Solutions Pvt. Ltd.',
    # 'images': ['static/description/banner.png'],
    'depends': ['project','hr', 'analytic','hr_timesheet','sale_crm','sale','instellars_custom_fields'],
    'data': [
        'views/project.xml',
        'views/timesheet_views.xml',
        
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

}
