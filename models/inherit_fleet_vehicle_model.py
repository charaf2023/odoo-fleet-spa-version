from odoo import models, fields


class FleetVehicleModels(models.Model):
    _inherit = 'fleet.vehicle.model'
    # Fields
    ptac = fields.Char("Poids total autorisé en charge (PTAC)", default="0")
    payload = fields.Char("Charge Utile ", default="0")
    image_128 = fields.Binary(read_only=False)




class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    # unique
    old_reg_card_nbr = fields.Char("N° d’immatriculation précédent", default="0",tracking=True)
    vin_sn = fields.Char("N° de Châssis",required=True,tracking=True)
    yr_of_first_reg = fields.Char("L'année de premiere mise en circulation", default="0")
    contracts_ids = fields.Many2many("fleet.vehicle.log.contract", string="Les contracts")
    spa_vehicle_type = fields.Selection([
        ('fonction', 'Véhicule de fonction'),
        ('service', 'Véhicule de service'),
        ('commercial', 'Véhicule commercial')
    ], default='fonction', required=True, string="Type de Véhicule",tracking=True)
    license_plate = fields.Char(required=True,tracking=True)
    category_id = fields.Many2one("fleet.vehicle.model.category", required=True,tracking=True)


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'
    #

    cost_frequency = fields.Selection(default="yearly")
    ins_ref = fields.Char(required=True,tracking=True)
    cost_subtype_id = fields.Many2one(required=True,tracking=True)
    start_date = fields.Date(required=True,tracking=True)
    expiration_date = fields.Date(required=True,tracking=True)
    assurance_company = fields.Char("Compagnie d'assurance")
