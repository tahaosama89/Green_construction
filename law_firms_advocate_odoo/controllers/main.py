# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'custom_project_count' in counters:
            values['custom_project_count'] = request.env['project.project'].search_count([]) \
                if request.env['project.project'].check_access_rights('read', raise_exception=False) else 0
        if 'custom_task_count' in counters:
            values['custom_task_count'] = request.env['project.task'].search_count([]) \
                if request.env['project.task'].check_access_rights('read', raise_exception=False) else 0
        return values
    
    @http.route(['/my/project/law_cases/<int:project_id>'], type='http', auth="user", website=True)
    def custom_portal_my_project_law_cases(self, project_id=None, access_token=None, **kw):
        try:
            project_sudo = self._document_check_access('project.project', project_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'project': project_sudo,
            'page_name': 'project'
        }
        return request.render(
            "law_firms_advocate_odoo.custom_portal_my_project_cases",
            values
        )