'''
Created on Aug 6, 2020

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

_view_arch = """
<data>
    <group name="attribute" position="inside">
        %s
    </group>    
</data>
"""


class AssetAttribute(models.Model):
    _name = 'account.asset.attribute'
    _description = 'Asset Attribute'
    _order = 'sequence,id'

    sequence = fields.Integer()
    active = fields.Boolean(default=True)
    field_id = fields.Many2one(
        'ir.model.fields', required=True, ondelete='cascade', delegate=True)
    category_ids = fields.Many2many('account.asset', string='Asset Model', domain=[
                                    ('state', '=', 'model')])

    @api.model
    def default_get(self, fields_list):
        res = super(AssetAttribute, self).default_get(fields_list)
        res.update({
            'model_id': self.env['ir.model']._get_id('account.asset'),
            'name': self.env['ir.sequence'].next_by_code(self._name),
        })

        return res

    @api.model
    def _update_view(self):
        res = []
        for record in self.search([('active', '=', True)]):
            if not record.category_ids:
                continue
            f = """<field name="%s" attrs="{'invisible' : [('category_id','not in', [%s])]}" /> """ % (
                record.name, ",".join(map(str, record.category_ids.ids)))
            res.append(f)
        arch = _view_arch % "\n        ".join(res)
        self.env.ref("oi_account_asset_tracking_e.view_account_asset_form_asset_tracking_attributes").sudo(
        ).write({'arch': arch})

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        res = super(AssetAttribute, self).create(vals_list)
        self._update_view()
        return res

    def write(self, vals):
        res = super(AssetAttribute, self).write(vals)
        self._update_view()
        return res

    def unlink(self):
        arch = _view_arch % ""
        self.env.ref("oi_account_asset_tracking_e.view_account_asset_form_asset_tracking_attributes").sudo(
        ).write({'arch': arch})
        res = super(AssetAttribute, self).unlink()
        self._update_view()
        return res

    def action_selections(self):
        return self.field_id.action_selections()

    def action_attributes(self):
        return self.field_id.action_attributes()

    def action_view_default(self):
        return self.field_id.action_view_default()
