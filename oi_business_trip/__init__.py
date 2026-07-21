from . import models

def post_init_hook(env):
    env["business.trip"]._create_approval_settings()
    
def uninstall_hook(env):
    env['approval.settings'].get("business.trip").unlink()    