{
    'name': 'SPA Fleet',
    'summary': 'spa fleet',
    'version': '1.0',
    'category': 'Uncategorized',
    'author': 'Charaf eddine Toumi',
    'website': 'https://www.spaelfath.com',
    'depends': ['mail','fleet','sale_management'],
    'data': [
            'security/ir.model.access.csv',
            'views/inherit_fleet_vehicle_model_form.xml',
            'views/tours.xml',
            'data/wilaya.xml',
            'data/communes.xml',
            'data/categories.xml',
            'data/intervention.xml'
    ],
    'demo': [],
    'sequence': -200,
    'installable': True,
    'auto_install': False,
}