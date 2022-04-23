{
    'name': 'Instellars Offer Release ',
    'version': '13.0.0.6',
    'category': 'Human Resources',
    
    'summary': 'Update Results and Create a Annexures',
    'description': "",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'hr',
        'hr_recruitment',
        'base',
        'crm',
        'web',
        'instellars_custom_fields',
        'hr_payroll',
    ],
    'data': [
    'security/ir.model.access.csv',
    'data/offer_letter_mail.xml',
    'data/appointment_letter.xml',
    'data/ref_sequencer.xml',
    'wizards/send_offer.xml',
    'views/hr_applicant.xml',
    'views/applicant_annexure_views.xml',
    'views/recruitment_stage.xml',
 
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False
}
