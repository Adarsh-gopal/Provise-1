# -*- coding: utf-8 -*-
{
    'name': 'Report Sales Person',
    'version': '13.0.1.0.0',
    'license': 'OPL-1',
    'category': 'Tools',
    'summary': 'Report Sales Person',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company':'Prixgen Tech Solutions Pvt. Ltd.',
    'website':'https://www.prixgen.com',
    'description': """
Report Sales Person
-------------------

Report Sales Person
""",
    'depends': ['account', 'account_reports'],
    'data': [
        'views/templates.xml',
        # 'views/filter.xml',
    ],
    'installable': True,
    'auto_install': False,
}
