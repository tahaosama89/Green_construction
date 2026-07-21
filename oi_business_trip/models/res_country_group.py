'''
Created on Jan 6, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CountryGroup(models.Model):
    _inherit = 'res.country.group'

    business_trip = fields.Boolean()
    
    extra_days = fields.Integer(string="Extra Days")
    
    country2_ids = fields.Many2many(related='country_ids', string='Countries (Related)')
    
    city_ids = fields.Many2many('res.city')
    
    code = fields.Char()
                        
    @api.onchange('country2_ids')
    def _onchange_country2_ids(self):
        if self.country_ids != self.country2_ids:
            self.country_ids = self.country2_ids
            

    @api.constrains('city_ids')
    def _check_city(self):
        for record in self:
            for city in record.city_ids._origin:
                if self.env['res.country.group'].search([('id','!=', record._origin.id), ('city_ids','=', city.id)]):
                    raise ValidationError(_("City in the country group MUST be unique %s ")%(city.name))