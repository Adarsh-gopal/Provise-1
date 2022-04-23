# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Split Invoice as Onsite or Offshore',
    'version': '13.0.0.9',
    'category': '',
    'summary': 'For all',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company':'Prixgen Tech Solutions Pvt. Ltd.',
    'website':'https://www.prixgen.com',
    'description': """
This module is display the fields .
    """,
    'depends': ['sale_timesheet','account','base','sale','sale_management'],
    'data': [
        'views/account_view.xml',
        'views/assets.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        "static/src/xml/sale_payment.xml",
       
    ],
   
    'installable': True,
    'auto_install': False
}
