{
    'name': 'Odoo Web Login Screen',
    'summary': 'The new configurable Odoo Web Login Screen',
    'version': '13.0.1.0',
    'category': 'Website',
    'summary': """The new configurable Odoo Web Login Screen""",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company':'Prixgen Tech Solutions Pvt. Ltd.',
    'website':'https://www.prixgen.com',
    'depends': [ 'web','website',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'views/website_templates.xml',
        'views/webclient_templates.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    
}
