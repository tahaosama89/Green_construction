# -*- coding: utf-8 -*-
from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    construction_request_id = fields.Many2one(
        'construction.material.request',
        string='Construction Material Request',
        copy=False,
        index=True,
    )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    construction_request_id = fields.Many2one(
        'construction.material.request',
        string='Construction Material Request',
        copy=False,
        index=True,
    )
