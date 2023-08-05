"""Class to manage user menus."""

from webhelpers2.html import literal
from sqlalchemy import select

from ..lib.i18n import _
from ..lib.utils import has_permission
from ..models import TRUE, DBSession
from ..models.groups import GROUP_USER
from ..models.storages import Storage, StorageUser
from ..models.projects import Project, ProjectUser, ProjectGroup
from ..models.tasks import Task
from ..models.jobs import Job


# =============================================================================
class Menu(object):
    """User menu management."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        self._request = request
        self._translate = request.localizer.translate
        self.active = 'user_id' in self._request.session

    # -------------------------------------------------------------------------
    def update(self):
        """Update the session with menu content."""
        if not self.active:
            return
        menu = []

        # Storages
        if has_permission(self._request, 'stg_user'):
            submenu = [
                self._entry(_('Advanced search'), 'file_search'),
                self._entry(_('All storages'), 'storage_index')] \
                if 'storage.index' in self._request.registry.settings \
                else [self._entry(_('All storages'), 'storage_index')]
            self._storage_entries(self._request.session['user_id'], submenu)
            menu.append(
                self._entry(_('Storages'), None, submenu, icon="storage"))

        # Projects
        if has_permission(self._request, 'prj_user'):
            submenu = [self._entry(_('All projects'), 'project_index')]
            self._project_entries(self._request.session['user_id'], submenu)
            menu.append(
                self._entry(_('Projects'), None, submenu, icon="project"))

        # Administration
        submenu = []
        if has_permission(self._request, 'admin'):
            submenu.append(self._entry(_('Site'), 'site_admin'))
        if has_permission(self._request, 'usr_editor'):
            submenu.append(self._entry(_('Users'), 'user_admin'))
        if has_permission(self._request, 'grp_editor'):
            submenu.append(self._entry(_('Groups'), 'group_admin'))
        if has_permission(self._request, 'stg_editor'):
            submenu.append(self._entry(_('Storages'), 'storage_admin'))
        if has_permission(self._request, 'idx_editor'):
            submenu.append(self._entry(_('Indexing'), 'indexer_admin'))
        if has_permission(self._request, 'prj_editor'):
            submenu.append(self._entry(_('Projects'), 'project_admin'))
        if submenu:
            menu.append(
                self._entry(_('Administration'), None, submenu, icon="admin"))

        self._request.session['menu'] = tuple(menu)

    # -------------------------------------------------------------------------
    def xhtml(self):
        """Return an <ul> structure with current entry highlighted."""
        if not self.active:
            return ''
        if 'menu' not in self._request.session:
            self.update()

        # Make XHTML
        menu = self._request.session['menu']
        html = u'<ul>{0}</ul>'.format(self._xhtml_entries(menu, 0))

        # Highlight current entry
        if 'breadcrumbs' in self._request.session:
            for crumb in reversed(self._request.session['breadcrumbs'][1:]):
                if crumb[1] is None:
                    continue
                params = dict(
                    (k, crumb[2][k]) for k in crumb[2] if k != '_anchor')
                path = self._request.route_path(crumb[1], **params)
                path = u'/'.join(path.split(u'/')[0:crumb[3] + 1])\
                       .replace('/edit/', '/view/')
                if u'href="{0}"'.format(path) in html:
                    html = html.replace(
                        u'<a class="slow" href="{0}"'.format(path),
                        u'<a class="slow current" href="{0}"'.format(path))
                    break

        # Tag current project
        if 'project' in self._request.session:
            path = self._request.route_path(
                'project_dashboard',
                project_id=self._request.session['project']['project_id'],
                _query={'id': self._request.session['project']['project_id']})
            html = html.replace(
                u'<li><a class="slow" href="{0}"'.format(path),
                u'<li class="active"><a class="slow" href="{0}"'.format(path))

        return literal(html)

    # -------------------------------------------------------------------------
    def _xhtml_entries(self, entries, depth):
        """Return <li> tags with entries.

        :param entries: (tuple)
            Tuple of entry tuples (See :meth:`_entry`)
        :param depth: (integer)
            Depth of entries in menu.
        """
        html = u''
        for entry in entries:
            tag = (depth == 0 and u'<strong>') \
                or (depth == 1 and entry[3] and u'<em>') or u''
            html += u'<li>' \
                + (u'<a class="slow" href="{0}">'.format(entry[2])
                   if entry[2] else '') \
                + tag \
                + (u'<img src="/Static/Images/{0}.png" alt="{0}"/> '.format(
                    entry[1]) if entry[1] else u'') + entry[0] \
                + tag.replace(u'<', u'</') \
                + (u'</a>' if entry[2] else u'')
            if entry[4]:
                html += u'<ul>{0}</ul>'.format(
                    self._xhtml_entries(entry[4], depth + 1))
            html += u'</li>'
        return html

    # -------------------------------------------------------------------------
    def _storage_entries(self, user_id, submenu):
        """Update menu entries for user storages shown in menu.

        :param user_id: (string)
            Current user ID.
        :param submenu: (list)
            Current submenu list.
        """
        # Look for user storages
        for storage in DBSession.query(Storage).join(StorageUser)\
                .filter(Storage.access != 'closed')\
                .filter(StorageUser.user_id == user_id)\
                .filter(StorageUser.in_menu == TRUE).order_by(Storage.label):
            submenu.append(self._entry(
                storage.label, 'storage_root', None, True,
                storage_id=storage.storage_id))

    # -------------------------------------------------------------------------
    def _project_entries(self, user_id, submenu):
        """Update menu entries for user projects shown in menu.

        :param user_id: (string)
            Current user ID.
        :param submenu: (list)
            Current submenu list.
        """
        groups = [k.group_id for k in DBSession.execute(
            select([GROUP_USER], GROUP_USER.c.user_id == user_id))]
        for project in DBSession.query(
                Project.project_id, Project.label, ProjectUser.perm,
                ProjectUser.entries).join(ProjectUser)\
                .filter(ProjectUser.user_id == user_id)\
                .filter(ProjectUser.in_menu == TRUE).order_by(Project.label):
            pid = project[0]
            subentries = [
                self._entry(_('Dashboard'), 'project_dashboard',
                            None, True, project_id=pid)]
            if project[3] in ('all', 'tasks') and \
               DBSession.query(Task.task_id).filter_by(project_id=pid).first()\
               is not None:
                subentries.append(self._entry(
                    _('Tasks'), 'task_index', None, True, project_id=pid))
            if project[3] in ('all', 'packs'):
                subentries.append(self._entry(
                    _('Packs'), 'pack_index', None, True, project_id=pid))
            subentries.append(self._entry(
                _('Last results'), 'build_results', None, True,
                project_id=pid))

            perm = 'leader' \
                if has_permission(self._request, 'prj_editor') else project[2]
            if perm != 'leader' and groups and 'leader' in \
                    [k[0] for k in DBSession.query(ProjectGroup.perm)
                     .filter_by(project_id=pid)
                     .filter(ProjectGroup.group_id.in_(groups))]:
                perm = 'leader'
            if perm == 'leader':
                if DBSession.query(Job.job_id).filter_by(project_id=pid)\
                   .first() is not None:
                    subentries.append(self._entry(
                        _('Background jobs'), 'job_index', None, True,
                        project_id=pid))
                subentries.append(self._entry(
                    _('Settings'), 'project_view', None, True, project_id=pid))

            submenu.append(self._entry(
                project[1], 'project_dashboard', tuple(subentries), True,
                project_id=pid, _query={'id': pid}))

    # -------------------------------------------------------------------------
    def _entry(self, label, route_name, subentries=None, is_minor=False,
               icon=None, **kwargs):
        """A menu entry tuple.

        :param label: (string)
            Label of the entry.
        :param route_name: (string)
            Name of the route for the link.
        :param subentries: (list, optional)
            List of subentries.
        :param is_minor: (boolean, default=False)
            Indicate whether this entry is a minor one.
        :param icon: (string, optional)
            Icon for this entry.
        :param kwargs: (dictionary)
            Keyworded arguments for :meth:`pyramid.request.Request.route_path`.
        :return: (tuple)
            A tuple such as
            ``(label, icon, url, is_minor, (subentry, subentry...))``.
        """
        return (self._translate(label), icon,
                route_name and self._request.route_path(route_name, **kwargs),
                is_minor, subentries and tuple(subentries))
