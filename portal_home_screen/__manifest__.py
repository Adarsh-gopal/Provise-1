{
    'name': 'Portal Home Screen Layout',
    'version': '13.0.0.13',
    'category': 'Portal',
    
    'summary': 'Grid View for Portal Home Page',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'web',
        'portal',
        'hr_org_chart',      
    ],
    'data': [
      
        'views/assets.xml',
        'views/portal.xml',
        # 'views/task_portal.xml',
 
    ],
    'qweb': [
        "static/src/xml/hr_portal_org_chart.xml",
        ],
    'installable': True,
    'application': True,
    'auto_install': False
}