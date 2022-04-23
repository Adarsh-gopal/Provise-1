{
    'name': 'HR Poratal Attendance',
    'version': '13.0.0.4',
    'category': 'Human Resources/Recruitment',
    
    'summary': 'Check-in/Check-out to Attendance as Portal Users',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'web',
        'hr_attendance',
        'hr',
        'website',
    ],
    'data': [
        'views/attendance_portal_template.xml',
        'views/assets.xml',
 
    ],
    # 'qweb': [
    #     "static/src/xml/formselection.xml",
    #     ],
    'installable': True,
    'application': True,
    'auto_install': False
}