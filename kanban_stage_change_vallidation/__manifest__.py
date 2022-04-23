{
    'name': 'Kanban stage change vallidation',
    'version': '13.0.0.12',    
    'summary': 'Confirm before changing stages',
    'description': "",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'depends': ['web','hr_recruitment','hr'],
    'data': [
        'data/ir_config_parameter.xml',
        'views/assets.xml',
        'views/hr_recruitment_form.xml',
        'views/recruitment_stage.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False
}
