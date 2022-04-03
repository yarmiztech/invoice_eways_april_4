# -*- coding: utf-8 -*-
{
    'name': "INVOICE EWAY April",
    'author':
        'ENZAPPS',
    'summary': """
This module is for eway einvoice Integration.
""",

    'description': """
        This module is for eway einvoice and Generating XML Report For Ledgers,Invoices,Vendor Bills.
    """,
    'website': "",
    'category': 'base',
    'version': '12.0',
    'depends': ['base', 'account','sale','enzapps_eway_einvoices',],
    'data': [
        'security/security.xml',
        'views/invoice.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
