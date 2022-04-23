{
    'name': 'Instellars Demand Management',
    'version': '13.0.0.3',
    'category': 'Human Resources',
    
    'summary': 'Required custom fields in employee module for instellars',
    'description': "",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'depends': [
        'base_setup',
        'crm',
        'hr',
        'instellars_custom_fields',
        'sale_management',
        'mail',
        'project',
    ],
    'data': [
        'data/demand_stage.xml',
        'wizard/convert_demand_to_opportunity.xml',
        'wizard/demand_opportunity_to_quotation.xml',
        'security/demand_security.xml',
        'security/ir.model.access.csv',
        'views/demand_stage_view.xml',
        'views/demands_view.xml',
        'views/sale_order_view.xml',
        'views/project_view.xml',

    ],
    
    'installable': True,
    'application': True,
    'auto_install': False
}
