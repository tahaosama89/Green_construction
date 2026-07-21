from odoo import SUPERUSER_ID
from odoo.api import Environment
from . import models
from . import wizard


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    use_state_id = env['account.asset']._get_use_state_id().id
    cr.execute("update account_asset set use_state_id=%s where use_state_id is null", [use_state_id])
