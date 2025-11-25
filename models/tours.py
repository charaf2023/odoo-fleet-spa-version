from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

########----TOURS MODEL ------#################

class Tours(models.Model):
    _name = 'fleet.vehicle.tours'
    _description = 'Tours'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'vehicle_id'

    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehicule", required=True, tracking=True,
                                 domain="[('state_id', '=', 'Disponible')]")
    driver_id = fields.Many2one(related="vehicle_id.driver_id", readonly=False, required=True)
    selected_driver_id = fields.Many2one('res.partner', defult=driver_id, required=True, string="Conducteur",
                                         tracking=True)

    tour_date = fields.Date(default=lambda self: fields.Date.today() + timedelta(days=1), string="Date", required=True,
                            tracking=True)
    tour_time = fields.Selection([
        ("morning", "MATIN"),
        ("afternoon", "APRÈS-MIDI"),
        ("day", "TOUT LA JOURNEE"),
    ], 'Période', required=True, default='morning', tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    priority = fields.Selection([
        ("0", "Low"),
        ("1", "Normal"),
        ("2", "High"),
        ("3", "Very High"),
    ], 'Priority', required=True, default='0', tracking=True)
    state = fields.Selection([
        ("not_confirmed", "Pas Confirmé"),
        ("confirmed", "Confirmé"),
        ("done", "Done"),
        ("cancelled", "Annuler"),
    ], 'Status', tracking=True)
    details = fields.Html(string="Details")
    tours_contracts_ids = fields.One2many("fleet.vehicle.tours.orders", "order_id", string="Les commandes",
    required=True, tracking=True)
    client_values = fields.Char(string='Clients', compute='_compute_extracted_clients', store=True,tracking=True)
    destination_values = fields.Char(string='Destinations', compute='_compute_extracted_destinations', store=True,tracking=True)


########----STATUS BUTTONS MULTI.. TREE ------#################
    def action_change_state_mul_confirmed(self):
        selected_records = self.env['fleet.vehicle.tours'].browse(self._context.get('active_ids'))
        all_records_have_specific_state = all(record.state == 'not_confirmed' for record in selected_records)
        if all_records_have_specific_state:
            for rec in selected_records:
                if rec.vehicle_id.state_id.name != "Disponible":
                    raise ValidationError("Véhicule indisponible (En panne) => " + str(rec.vehicle_id.name))
                else:
                    rec.state = "confirmed"
        else:
            raise ValidationError("ERROR: Tous les enregistrements doivent être non confirmés!")

    def action_change_state_mul_done(self):
        selected_records = self.env['fleet.vehicle.tours'].browse(self._context.get('active_ids'))
        all_records_have_specific_state = all(record.state == 'confirmed' for record in selected_records)
        if all_records_have_specific_state:
            for record in selected_records:
                record.state ="done"
        else:
            raise ValidationError("ERROR: Tous les enregistrements doivent être confirmés")
        

    def action_change_state_mul_cancel(self):
        selected_records = self.env['fleet.vehicle.tours'].browse(self._context.get('active_ids'))
        all_records_have_specific_state = all(record.state == 'confirmed' for record in selected_records)
        if all_records_have_specific_state:
            for record in selected_records:
                record.state ="cancelled"
        else:
            raise ValidationError("ERROR: Tous les enregistrements doivent être confirmés")

    def action_change_state_mul_restore(self):
        selected_records = self.env['fleet.vehicle.tours'].browse(self._context.get('active_ids'))
        all_records_have_specific_state = all(record.state == 'cancelled' for record in selected_records)
        if all_records_have_specific_state:
            for record in selected_records:
                record.state ="not_confirmed"
        else:
            raise ValidationError("ERROR: Tous les enregistrements doivent être annulés")

    ########----FORM CONSTRAINS ------#################

    @api.constrains('vehicle_id', 'selected_driver_id', 'tour_date', 'tour_time', 'tours_contracts_ids')
    def _check_conflicting_tours(self):
        domain = [('state', 'in', ['not_confirmed', 'confirmed'])]
        records = self.search(domain)
        print(len(records))
        print(records)
        same_driver_cond = False
        same_vehicle_cond = False
        result = False
        for record in records:
            if record.id == self.id:
                records -= record
        print(records)
        len_rec = len(records)

        if len(self.tours_contracts_ids) == 0:
            raise ValidationError("ERROR: Entrez N° de commande")
        if len_rec == 0:
            print("DONE:**********************")
            self.state = "not_confirmed"
            return
        if len_rec > 0:
            for i in range(len(records)):
                same_driver_cond = self.selected_driver_id.name == records[
                    i].driver_id.name  # Compare the IDs instead of names
                same_vehicle_cond = self.vehicle_id.name == records[
                    i].vehicle_id.name  # Compare the IDs instead of names
                same_date_cond = self.tour_date == records[i].tour_date
                same_time_cond = not (
                        (self.tour_time == "morning" and records[i].tour_time == "afternoon") or
                        (self.tour_time == "afternoon" and records[i].tour_time == "morning"))
                result = (same_driver_cond or same_vehicle_cond) and same_time_cond and same_date_cond
                # print result
                print("driver--------------vehicle-----------------date---------------time :  " + i.__str__())
                print(str(self.selected_driver_id.name) + "----" + str(self.vehicle_id.name) + "----" + str(
                    self.tour_date) + "----" + str(self.tour_time))
                print(str(records[i].driver_id.name) + "----" + str(records[i].vehicle_id.name) + "----" + str(
                    records[i].tour_date) + "----" + str(records[i].tour_time))
                ###print cond states
                print("driver cond:@" + str(same_driver_cond))
                print("vehicle cond:@" + str(same_vehicle_cond))
                print("date cond:@" + str(same_date_cond))
                print("time cond:@" + str(same_time_cond))
                print("result" + str(result))
                # condd
                if result:
                    print("CONFLICT FOUND!!!!:**********************")
                    break
                else:
                    print("NOT FOUND")

            if not result:
                print("DONE:**********************")
                self.state = "not_confirmed"

            if result:  ######display error
                error = ""
                time_error = ""
                if self.tour_time == "morning": time_error = "MATIN"
                if self.tour_time == "afternoon": time_error = "APRÈS-MIDI"
                if self.tour_time == "afternoon": time_error = "TOUT LA JOURNEE"
                if same_driver_cond and same_vehicle_cond:
                    error = "La véhicule " + str(self.vehicle_id.name) + " et le conducteur " + str(
                        self.selected_driver_id.name) + "  ne sont pas disponibles le: (" + str(
                        self.tour_date) + "/" + time_error + ")."
                elif same_vehicle_cond:
                    error = "La véhicule " + str(self.vehicle_id.name) + "n'est pas disponible le: (" + str(
                        self.tour_date) + "/" + time_error + ")."
                elif same_driver_cond:
                    error = "Le conducteur " + str(self.selected_driver_id.name) + "n'est pas disponible le: (" + str(
                        self.tour_date) + "/" + time_error + ")."
                raise ValidationError("ERROR: " + error)

    ########----DRIVER TRICK FOR CHANGING RELATED FIELD KEEP STICKY----#################

    @api.onchange('vehicle_id')
    def onchange_(self):
        if self.driver_id:
            self.selected_driver_id = self.driver_id
            print("CHANGED TO ***********" + self.selected_driver_id.name)

    ########----CALC OF DEST+CLIENT TREE FIELDS---#################

    @api.depends('tours_contracts_ids.client_id')
    def _compute_extracted_clients(self):
        for record in self:
            client_values = ", ".join([child_record.client_id.name for child_record in record.tours_contracts_ids if
                                       child_record.client_id.name])
            record.client_values = client_values

    @api.depends('tours_contracts_ids.wilaya_id', 'tours_contracts_ids.commune_id')
    def _compute_extracted_destinations(self):
        for record in self:
            destination_values = []
            for line in record.tours_contracts_ids:
                if line.wilaya_id and line.commune_id:
                    commune_name = str(line.commune_id.name).split('-')[1]
                    destination = f"({line.wilaya_id.name}/{commune_name})"
                    destination_values.append(destination)
            record.destination_values = ", ".join(destination_values)

    ########----STATUS BUTTONS FORM ------#################

    def action_tours_not_confirmed(self):
        for rec in self:
            rec.state = "not_confirmed"

    def action_tours_done(self):
        for rec in self:
            rec.state = "done"

    def action_tours_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_tours_confirmed(self):
        for rec in self:
            if rec.vehicle_id.state_id.name != "Disponible":
                raise ValidationError("ERROR: Véhicule indisponible (En panne) => " + str(rec.vehicle_id.name))
            else:
                rec.state = "confirmed"

########----TOURS MODEL ------#################

class ToursOrders(models.Model):
    _name = "fleet.vehicle.tours.orders"
    _description = "Tours orders"
    _rec_name = "order_number"

    order_id = fields.Many2one("fleet.vehicle.tours")
    order_number = fields.Char(string="N° de commande", required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    wilaya_id = fields.Many2one('fleet.wilaya', string='Wilaya', required=True,tracking=True)
    commune_id = fields.Many2one('fleet.commune', string='Commune', domain="[('wilaya_id', '=', wilaya_id)]",
                                 required=True,tracking=True)

    ########----CLEAN COMMUNE IF WILAYA CHANGED ------#################

    @api.onchange('wilaya_id')
    def _onchange_client(self):
        if self.wilaya_id:
            self.commune_id = False


#######-------WILAYA AND COMMUNE MODELS------########
class Wilaya(models.Model):
    _name = 'fleet.wilaya'

    name = fields.Char(string='Wilaya')
    communes_ids = fields.One2many('fleet.commune', 'wilaya_id', string='Communes')


class Commune(models.Model):
    _name = 'fleet.commune'

    name = fields.Char(string='Commune')
    wilaya_id = fields.Many2one('fleet.wilaya', string='Wilaya')
