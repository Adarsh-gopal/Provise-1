{
    'name': 'tree view customizations',
    'version': '13.0.0.1',
    'category': 'others',
    
    'summary': 'tree view customizations',
    'description': "",
     'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'hr',
        'web',
        'sale',
        'sale_crm',
        'account',
        'instellars_custom_fields',
        'project',
        'hr_appraisal'
    ],
    'data': [
    'views/sale_order_tree.xml',
    'views/invoice_tree_view.xml',
    'views/employee_tree_view.xml',
    'views/hr_appraisal_tree.xml',
    'views/project_tree_views.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False
}
