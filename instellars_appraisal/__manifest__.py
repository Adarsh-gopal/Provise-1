{
    'name': 'Instellars Appraisal Customizations',
    'version': '13.0.0.3',
    'category': 'Human Resources',
    
    'summary': 'Required custom fields in employee module for instellars',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'sign',
        'hr_appraisal',
        'instellars_offer_release',
        'base',
        ],
    'data': [
        'data/appraisal_sequence.xml',
        'data/mail_data.xml',
        'security/ir.model.access.csv',
        'security/manager_group.xml',
        'views/hr_appraisal.xml',
        'views/annexures_view_form.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False
}
