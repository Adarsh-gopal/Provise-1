{
    'name': 'Instellars Timesheet Report',
    'version': '13.0.0.9',
    'category': 'Human Resources/Recruitment',
    
    'summary': 'Timesheet Report',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'sale_timesheet_enterprise',
        'hr_timesheet',
        'timesheet_grid',   
        'portal_timesheet',   
    ],
    'data': [
        # 'security/hr_timesheet_security.xml',
        'data/mail_data.xml',
        'wizards/timesheet_report_wiz.xml', 
        'views/hr_timesheet.xml', 
    ],
    # 'qweb': [
    #     "static/src/xml/formselection.xml",
    #     ],
    'installable': True,
    'application': True,
    'auto_install': False
}