{
    'name': 'HR Portal Timesheet',
    'version': '13.0.0.23',
    'category': 'Human Resources/Recruitment',
    
    'summary': 'Portal Timesheet',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'sale_timesheet_enterprise',
        'hr_timesheet',
        'project',
        'timesheet_grid',      
    ],
    'data': [
        'security/hr_timesheet_security.xml',
        'views/assets.xml',
        'views/timesheet_portal_view.xml',
        'views/hr_employee_view.xml',
        'views/task_portal.xml',
        'views/team_timesheet.xml',
        'wizards/timesheet_validation_view.xml',
 
    ],
    'qweb': [
        "static/src/xml/base.xml",
        ],
    'installable': True,
    'application': True,
    'auto_install': False
}