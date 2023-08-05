"""Maintenance view callables."""

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED


# =============================================================================
@view_config(route_name='maintenance', renderer='../Templates/maintenance.pt',
             permission=NO_PERMISSION_REQUIRED)
def mainatenance_view(request):
    """Maintenance view.

    :type  request: pyramid.request.Request
    :param request:
        Current request.
    """
    if request.registry.settings.get('maintenance') != 'true':
        return HTTPFound(request.route_path('home'))
    request.session.clear()
    return {}
