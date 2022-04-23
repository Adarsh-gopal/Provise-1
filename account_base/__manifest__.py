# -*- coding: utf-8 -*-
{
    'name': "account_base_1.0 For Instellars",

    'summary': """
        Base Customization on Accounting""",

    'description': """
            Included Functionalities -
                1) Roundoff.-------------------------------------------(roundoff.py/xml)
                2) Dimension-------------------------------------------(account_account.py/xml,account_cost_center.py/xml,account_general_ledger.py,
                                                                        account_invoice.py/xml,account_invoice_line.py,account_invoice_report.py/xml,
                                                                        account_move_line.py/xml,report_financial.xml)
                3) Unrelate Bill Date and Accounting date--------------(disconnect.py)
                4) Currency Inverse and precision----------------------(currency_inverce.py)
            """,

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company':'Prixgen Tech Solutions Pvt. Ltd.',
    'website':'https://www.prixgen.com',

    'category': 'Customization',
    'version': '13.0.1.2',

    'depends': ['base','account','account_reports'],

    'data': [
        'security/ir.model.access.csv',
        'security/account_cost_center_security.xml',
        
        'data/account_financial_report_data.xml',
        'views/account_invoice_report.xml',
        'views/account_cost_center.xml',
        'views/account_move_line.xml',
        'views/report_financial.xml',
        'views/currency_inverse.xml',
        'views/account_account.xml',
        'views/account_invoice.xml',
        # 'views/round_off.xml'
    ],
}
