{
    'name': "Updates",
    'description': """Updates in project mobishop""",
    'author': "Veronica Safwat",
    "license": "AGPL-3",
    'website': "",
    'category': 'Uncategorized',
    'version': '15.0',
    'depends': ['base','stock','purchase','product','sale','account'],

    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/stock_move.xml',
        'views/stock_quant.xml',
        'views/purchase_order.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
        'views/account_bank_statement.xml',
        'views/res_partner_category.xml',
        'reports/saleorder_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
