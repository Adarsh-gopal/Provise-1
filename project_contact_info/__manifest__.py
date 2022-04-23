{
    'name': 'Contact information for  project',
    'version': '13.0.0.2',
    'category': 'Project',
    
    'summary': 'contact information related for perticular projects',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company':'Prixgen Tech Solutions Pvt. Ltd.',
    'website':'https://www.prixgen.com',
    'depends': [
        'hr',
        'hr_recruitment',
        'hr_skills',
        'base',
        'crm',
        'project',
       
    ],
    'data': [
    'security/ir.model.access.csv',
    'views/assets.xml',
    'views/project_view.xml',
    ],
    'qweb': [
        'static/src/xml/resume_templates.xml',
        'static/src/xml/skills_templates.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False
}
