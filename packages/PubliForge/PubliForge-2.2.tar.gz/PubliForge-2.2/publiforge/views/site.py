# pylint: disable = C0322
"""Site view callables."""

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden

from ..lib.xml import upload_configuration, export_configuration
from ..lib.i18n import _
from ..lib.utils import has_permission
from ..lib.viewutils import get_action
from ..models import DBSession, close_dbsession
from ..models.users import User
from ..models.groups import Group
from ..models.storages import Storage
from ..models.indexers import Indexer
from ..models.processors import Processor
from ..models.projects import Project


# =============================================================================
class SiteView(object):
    """Class to manage global website."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='site_admin', renderer='../Templates/sit_admin.pt',
                 permission='sit.adm')
    def admin(self):
        """List users, groups, storages, processors and projects and allow
        import/export operations."""

        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'admin')
            action = ''
        elif action[0:4] == 'exp!':
            return self._export_site(items)

        fbuild = self._request.registry['fbuild']
        fbuild.refresh_agent_list(self._request)

        quantity = {'users': DBSession.query(User).count(),
                    'groups': DBSession.query(Group).count(),
                    'storages': DBSession.query(Storage).count(),
                    'indexers': DBSession.query(Indexer).count(),
                    'projects': DBSession.query(Project).count()}

        self._request.breadcrumbs.add(_('Site administration'), 2)
        return {
            'action': action, 'agent_urls': fbuild.agent_urls(),
            'db': (DBSession.bind.name, DBSession.bind.url.database),
            'processor_ids': sorted(Processor.ids(self._request)),
            'opener_ids': self._request.registry['opener'].ids(),
            'quantity': quantity}

    # -------------------------------------------------------------------------
    def _export_site(self, objects):
        """Export site.
        :param objects: (list)
            List of objects to export.
        :return: (:class:`pyramid.response.Response` instance)
        """
        if not has_permission(self._request, 'admin'):
            raise HTTPForbidden()

        elements = []
        for obj in objects:
            if obj == 'users':
                for user in DBSession.query(User).order_by('login'):
                    elements.append(user.xml(True))
            elif obj == 'groups':
                for group in DBSession.query(Group).order_by('group_id'):
                    elements.append(group.xml())
            elif obj == 'storages':
                for storage in DBSession.query(Storage).order_by('storage_id'):
                    elements.append(storage.xml())
            elif obj == 'indexers':
                for indexer in DBSession.query(Indexer).order_by('indexer_id'):
                    elements.append(indexer.xml())
            elif obj == 'projects':
                for project in DBSession.query(Project).order_by('label'):
                    elements.append(project.xml(self._request))

        name = self._request.registry.settings.get('skin.name', 'publiforge')
        name = '%s_%s.pf%s' % ((name, objects[0], objects[0][0])) \
            if len(objects) == 1 else '%s.pf' % name
        return export_configuration(elements, name)
