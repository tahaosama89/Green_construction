# -*- coding: utf-8 -*-
'''
model tender item
'''
from odoo import models, fields, api, _

class TenderItem(models.Model):
    _name = 'tender.item'
    _description = 'tender.item'
    _rec_name = "name"

    name = fields.Char(string=_("Name"))
    job_id = fields.Many2one('tender.job', string=_("Related Job"))
    image = fields.Image(string=_("Image"))
    uom_id = fields.Many2one('uom.uom', string=_("Unit Of Measure"))
    code = fields.Char(string=_("Code"))
    repeated = fields.Boolean(string=_('Repeated'), help='Repeated', copy=True, default=False)
    analytic_tag = fields.Many2many('account.account.tag', string=_('Analytic Tag'))
    related_product_id = fields.Many2one('product.product', string=_('Related Product'), readonly=True)

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', _('Code must be unique')),
        ('unique_name', 'UNIQUE(name)', _('Name must be unique')),
    ]

    @api.model
    def create(self, values):
        """Create a new 'tender.item' record with a unique name."""
        tender_item = super(TenderItem, self).create(values)
        product_values = {
            'name': tender_item.name,
            'detailed_type': 'service',
        }
        product = self.env['product.product'].create(product_values)
        tender_item.write({'related_product_id': product.id})
        return tender_item

    def unlink(self):
        """
        Delete the current record if its state is 'draft'.
        """
        for tender_item in self:
            if tender_item.related_product_id:
                tender_item.related_product_id.active = False
        return super(TenderItem, self).unlink()