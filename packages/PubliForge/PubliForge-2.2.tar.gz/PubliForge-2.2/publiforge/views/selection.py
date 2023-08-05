"""Selection view callables."""

from os import sep
from os.path import exists, join
from time import time
from webhelpers2.html import literal

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from ..lib.i18n import _
from ..lib.utils import has_permission
from ..models import DBSession, close_dbsession
from ..models.users import UserFile
from ..models.storages import Storage


# =============================================================================
class Selection(object):
    """User selection management."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        self._request = request
        self.active = has_permission(self._request, 'stg_user')

    # -------------------------------------------------------------------------
    def update(self):
        """Update the list of files of the user selection sorted by storage."""
        # pylint: disable = no-member
        if not self.active:
            return
        selection = self._request.session.get('selection')
        overviews = \
            dict([(k, selection[0][k][2]) for k in selection[0]]) \
            if selection else {}
        selection = {}

        storage_root = self._request.registry.settings['storage.root']
        storage = {'storage_id': None}
        files = sorted([k[0] for k in DBSession.query(UserFile.path).filter_by(
            user_id=self._request.session['user_id']).all()])
        for path in files:
            if not exists(join(storage_root, path)):
                DBSession.query(UserFile).filter_by(path=path).delete()
                continue
            sid = path.partition(sep)[0]
            path = path.partition(sep)[2]
            if sid != storage['storage_id']:
                storage = DBSession.query(Storage).filter_by(
                    storage_id=sid).first()
                if storage is None:
                    storage = {'storage_id': None}
                    continue
                selection[sid] = (storage.label, [], overviews.get(sid, False))
                storage = {
                    'storage_id': sid, 'openers': [
                        k.opener_id for k
                        in sorted(storage.openers, key=lambda k: k.sort)]}
            opener, content = self._request.registry['opener'].get_opener(
                join(storage_root, sid, path), storage)
            selection[sid][1].append((
                path, opener and
                opener.overview(self._request, storage, path, content),
                opener and
                opener.title(self._request, storage, path, content)))

        DBSession.commit()
        self._request.session['selection'] = (
            selection, time() +
            int(self._request.registry.settings.get('storage.cache', 3600)))

    # -------------------------------------------------------------------------
    def invalidate(self):
        """Invalidate the current selection if exists."""
        if 'selection' in self._request.session:
            self._request.session['selection'] = (
                self._request.session['selection'][0], 0)

    # -------------------------------------------------------------------------
    def toggle_overview(self, storage_id):
        """Toggle overview for storage ``storage_id``.

        :param storage_id: (string)
            Storage ID.
        """
        if 'selection' in self._request.session and \
           storage_id in self._request.session['selection'][0]:
            item = self._request.session['selection'][0][storage_id]
            self._request.session['selection'][0][storage_id] = (
                item[0], item[1], not item[2])

    # -------------------------------------------------------------------------
    def xhtml(self):
        """Return an <ul> structure or a <span> structure if empty."""
        if not self.active:
            return ''
        if 'selection' not in self._request.session or \
           self._request.session['selection'][1] < time():
            self.update()
        selection = self._request.session['selection'][0]
        translate = self._request.localizer.translate

        # Empty selection
        if not selection:
            return translate(_('Your selection is empty.'))

        # Browse storage/file
        html = ''
        tag = 'span' if self._request.is_xhr else 'a'
        for sid in sorted(selection):
            overview = selection[sid][2]
            html_storage = u'<li>\n<div class="storage">'\
                '<input type="checkbox" value="1" class="selectAll"/> '\
                '<{tag} {href_prefix}href="{rm_url}" title="{rm_title}"'\
                ' class="selectionTool">'\
                '<img src="/Static/Images/selection_remove_one.png"'\
                ' alt="remove"/></{tag}> '\
                '<{tag} {href_prefix}href="{ov_url}" title="{ov_title}"'\
                ' class="selectionTool">'\
                '<img src="/Static/Images/overview_{on_off}.png"'\
                ' alt="overview"/></{tag}> '\
                '<a href="{url}"><strong>{title}</strong></a></div>\n'\
                '<ul>\n'.format(
                    tag=tag,
                    href_prefix=self._request.is_xhr and 'data-' or '',
                    rm_url=self._request.route_path(
                        'selection_rm_storage', storage_id=sid),
                    rm_title=translate(_('Remove files of this storage')),
                    ov_url=self._request.route_path(
                        'selection_overview', storage_id=sid),
                    ov_title=translate(
                        overview and _('Hide overviews') or
                        _('Show overviews')),
                    on_off=overview and 'on' or 'off',
                    url=self._request.route_path(
                        'storage_root', storage_id=sid),
                    title=selection[sid][0])
            for item in selection[sid][1]:
                html_storage += u'<li>'\
                    '<input type="checkbox" value="1" name="~{path}"/> '\
                    '<{tag} {href_prefix}href="{rm_url}" title="{rm_title}"'\
                    ' class="selectionTool">'\
                    '<img src="/Static/Images/selection_remove_one.png"'\
                    ' alt="remove"/></{tag}> '\
                    '<a href="{url}" class="selectionFile" draggable="true"'\
                    ' title="{path}" data-path="{path}"'\
                    '{data_title}>{title}</a>{overview}</li>\n'.format(
                        path=join(sid, item[0]), tag=tag,
                        href_prefix=self._request.is_xhr and 'data-' or '',
                        rm_url=self._request.route_path(
                            'selection_rm_file', storage_id=sid, path=item[0]),
                        rm_title=translate(_('Remove this file')),
                        url=self._request.route_path(
                            'file_render', storage_id=sid, path=item[0]),
                        title=not overview and item[2] or item[0].replace(
                            '/', ' / '),
                        data_title=item[2] and u' data-title="{0}"'.format(
                            item[2]) or '',
                        overview=overview and item[1] and
                        u'<div class="overview">{0}</div>'.format(
                            item[1]) or '')
            html_storage += u'</ul>\n</li>\n'
            html += html_storage
        return literal(u'<ul>\n%s</ul>' % html)

    # -------------------------------------------------------------------------
    def add(self, paths):
        """Add files to the selection.

        :param paths: (list)
            List of files to add.
        """
        user_id = self._request.session['user_id']
        old_paths = [k[0] for k in DBSession.query(UserFile.path).filter_by(
            user_id=user_id).filter(UserFile.path.in_(paths)).all()]
        for path in set(paths) - set(old_paths):
            DBSession.add(UserFile(path, user_id))
        DBSession.commit()
        self.invalidate()


# =============================================================================
class SelectionView(object):
    """Class to manage user selection views."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='selection_rm_storage')
    @view_config(route_name='selection_rm_file')
    @view_config(route_name='selection_rm_storage', renderer='json', xhr=True)
    @view_config(route_name='selection_rm_file', renderer='json', xhr=True)
    def remove(self):
        """Remove files from the user selection."""
        # Remove file from selection
        storage_id = self._request.matchdict.get('storage_id')
        path = self._request.matchdict.get('path')
        query = DBSession.query(UserFile).filter_by(
            user_id=self._request.session['user_id'])
        if storage_id and path:
            query = query.filter_by(path=join(*((storage_id,) + path)))
        elif storage_id:
            query = query.filter(
                UserFile.path.ilike('%s%s%%' % (storage_id, sep)))
        query.delete('fetch')
        DBSession.commit()

        # Send response
        selection = Selection(self._request)
        selection.invalidate()
        if self._request.is_xhr:
            return selection.xhtml()
        raise HTTPFound(self._request.breadcrumbs.current_path())

    # -------------------------------------------------------------------------
    @view_config(route_name='selection_overview')
    @view_config(route_name='selection_overview', renderer='json', xhr=True)
    def overview(self):
        """Toggle overview of files for the indicated storage."""
        selection = Selection(self._request)
        selection.toggle_overview(self._request.matchdict.get('storage_id'))
        if self._request.is_xhr:
            return selection.xhtml()
        raise HTTPFound(self._request.breadcrumbs.current_path())

    # -------------------------------------------------------------------------
    @view_config(route_name='selection_add')
    @view_config(route_name='selection_add', renderer='json', xhr=True)
    def add(self):
        """Add one file to the user selection with an AJAX request."""
        if not self._request.is_xhr:
            raise HTTPForbidden()

        storage_root = self._request.registry.settings['storage.root']
        path = join(*self._request.matchdict.get('path'))
        if not exists(join(storage_root, path)):
            return Selection(self._request).xhtml()

        user_file = DBSession.query(UserFile).filter_by(
            user_id=self._request.session['user_id'], path=path).first()
        if user_file is not None:
            return Selection(self._request).xhtml()

        DBSession.add(UserFile(path, self._request.session['user_id']))
        DBSession.commit()
        selection = Selection(self._request)
        selection.invalidate()
        return selection.xhtml()
