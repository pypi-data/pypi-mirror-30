# -*- coding: utf-8 -*-
"""File view callables."""

from os.path import join, exists, isdir, splitext, dirname, relpath
from time import time, sleep
from colander import Mapping, SchemaNode, String
from colander import Length
from webhelpers2.html import literal
# pylint: disable = no-name-in-module
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, XmlLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
# pylint: enable = no-name-in-module

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.response import Response

from .selection import Selection
from ..lib.i18n import _
from ..lib.utils import MIME_TYPES, get_mime_type, normalize_filename, age
from ..lib.viewutils import get_action, current_storage, file_download
from ..lib.viewutils import dbquery_storages
from ..lib.viewutils import vcs_user, save_vcs_user
from ..lib.packutils import create_pack
from ..lib.form import Form
from ..lib.paging import PAGE_SIZES, Paging
from ..lib.filter import Filter
from ..models import NULL, ID_LEN, DESCRIPTION_LEN, PATH_LEN
from ..models import DBSession, close_dbsession
from ..models.storages import Storage
from ..models.indexers import Indexer


CSV_DELIMITER = '\t'


# =============================================================================
class FileView(object):
    """Class to manage files in a storage."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(
        route_name='file_search', renderer='../Templates/fil_search.pt',
        permission='stg.read')
    def search(self):
        """Search files in storages.

        ``session['search']`` is a dictionary with the following keys:
        ``scope``,  ``inputs``, ``columns`` and ``result``.
        """
        # Scope, filter and form
        action, items = get_action(self._request)
        scope = self._search_scope()
        wfilter, result_columns = self._search_filter(action)
        form = self._search_form()

        # Form and action
        session = self._request.session
        if action[0:4] == 'dnl!':
            name = len(items) > 1 and _('search_${t}.zip', {'t': int(time())})
            return file_download(
                self._request, self._request.registry.settings['storage.root'],
                items, name and self._request.localizer.translate(name))
        elif action[0:4] == 'npk!' and 'project' in session:
            items = create_pack(self._request, items)
            if items[0] is not None:
                return HTTPFound(self._request.route_path(
                    'pack_edit', project_id=items[0], pack_id=items[1],
                    _anchor='tab0'))
        elif action[0:4] == 'sel!':
            Selection(self._request).add(items)
        elif action == 'crm!all':
            wfilter.clear()

        # Paging parameters
        sort = self._request.params.get('sort') or \
            'paging' in session and \
            'search' in session['paging'][1] and \
            session['paging'][1]['search']['sort'] or '-score'
        Paging.params(self._request, 'search', sort)

        # Results
        results = None
        if 'filter' in self._request.params or action[:4] == 'crm!':
            results = self._search_execute(wfilter, self._request.params)
        elif 'search' in session:
            results = session['search']['result']
            if 'sort' in self._request.params:
                results = sorted(
                    results,
                    key=lambda k: k.get(sort[1:], ''), reverse=sort[0] == '-')
        if action[0:4] == 'csv!':
            name = _('search_${t}.csv', {'t': int(time())})
            return self._search_export_csv(
                results, items, result_columns,
                self._request.localizer.translate(name))

        self._request.breadcrumbs.add(_('Advanced search'))
        return {
            'scope': scope, 'wfilter': wfilter,
            'result_columns': result_columns, 'form': form,
            'MIME_TYPES': MIME_TYPES, 'PAGE_SIZES': PAGE_SIZES,
            'paging': results is not None and Paging(
                self._request, 'search', results) or None}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='file_read', renderer='../Templates/fil_display.pt',
        permission='stg.read')
    @view_config(
        route_name='file_render', renderer='../Templates/fil_display.pt',
        permission='stg.read')
    def display(self):
        """Display content or rendering."""
        storage, handler = current_storage(self._request)
        path, filename, fullname, opener, content = self._file_opener(storage)
        if fullname is None:
            return HTTPFound(self._request.route_path(
                'storage_browse', storage_id=storage['storage_id'], path=path))
        if opener is None:
            return self.download()

        # Action
        form = self._display_form()
        action, items, working = self._display_action(
            form, storage, handler, dirname(path), filename)
        refresh = self._request.registry.settings.get('refresh.short', '2')
        if action == 'npk!' and items[0] is not None:
            return HTTPFound(self._request.route_path(
                'pack_edit', project_id=items[0], pack_id=items[1],
                _anchor='tab0'))
        elif action == 'sel!':
            Selection(self._request).add((join(storage['storage_id'], path),))
        elif action == 'dup!':
            sleep(int(refresh))
            if not self._request\
                    .registry['handler'].progress((storage['storage_id'],))[0]:
                filename = normalize_filename(
                    items[0], handler.normalize_mode) \
                    if handler.normalize_mode is not None else items[0]
                filename = filename if filename else items[0]
                return HTTPFound(self._request.route_path(
                    'file_render', storage_id=storage['storage_id'],
                    path=join(dirname(path), filename)))
        working = self._request\
            .registry['handler'].progress((storage['storage_id'],), working)[0]
        if working:
            self._request.response.headerlist.append(('Refresh', refresh))

        # Read or render
        html = ''
        mode = 'read' if '/read/' in self._request.current_route_path() \
            else 'render'
        if mode == 'render' and opener.can_render():
            html = opener.render(self._request, storage, path, content)
            if 'keep' not in self._request.params:
                self._pop_read_write_routes(storage)
                self._request.breadcrumbs.add(_('File rendering'))
            else:
                self._request.breadcrumbs.add(_('File rendering'), keep=True)
        if not html:
            mode = 'read'
            html = opener.read(self._request, storage, path, content)
            self._pop_read_write_routes(storage)
            self._request.breadcrumbs.add(_('File content'))

        return {
            'form': form, 'action': action, 'storage': storage, 'path': path,
            'filename': filename, 'mime_type': get_mime_type(fullname),
            'opener': opener, 'mode': mode, 'content': html,
            'position': opener.position(dirname(fullname), filename),
            'searches': self._search_results(storage, path)}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='file_write', renderer='../Templates/fil_modify.pt',
        permission='stg.read')
    @view_config(
        route_name='file_edit', renderer='../Templates/fil_modify.pt',
        permission='stg.read')
    def modify(self):
        """Modify file and save it."""
        storage = current_storage(self._request)[0]
        path, filename, fullname, opener, content = self._file_opener(storage)
        if opener is None or not opener.can_write():
            return HTTPFound(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path=path))
        if storage['perm'] != 'writer':
            self._request.session.flash(
                _("You can't modify this storage!"), 'alert')
            return HTTPFound(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path=path))

        # Actions
        preview = description = None
        action = get_action(self._request)[0]
        if action[0:4] == 'des!':
            description = opener.information(self._request, action[4:])
            if self._request.is_xhr:
                return Response(description, content_type='text/html')

        html = ''
        native = None
        mode = 'write' if '/write/' in self._request.current_route_path() \
            else 'edit'
        self._pop_read_write_routes(storage)
        if (action == 'edt!' or (mode == 'edit' and action != 'wrt!')) \
           and opener.can_edit():
            mode = 'edit'
            form, html, native = opener.edit(
                self._request, action, storage, path, content)
            if html:
                self._request.breadcrumbs.add(_('File editing'))
        if not html:
            mode = 'write'
            form, html, content = opener.write(
                self._request, storage, path, content)
            self._request.breadcrumbs.add(_('File writing'))

        if action == 'pre!' and not self._request.session.peek_flash('alert') \
           and opener.can_render():
            preview = opener.render(
                self._request, storage, path, content, native)

        # Save
        save_vcs_user(self._request, storage)
        if 'vcs_change' not in self._request.params \
                and (action == 'sav!' or action == 'sac!') \
                and form.validate() \
                and opener.save(self._request, storage, path,
                                content, form.values):
            self._request.session.flash(_('"${f}" saved.', {'f': path}))
            if action == 'sav!':
                return HTTPFound(self._request.route_path(
                    'file_render', storage_id=storage['storage_id'],
                    path=path))

        return {
            'form': form, 'action': action, 'storage': storage, 'path': path,
            'filename': filename, 'mime_type': get_mime_type(fullname),
            'opener': opener, 'mode': mode, 'content': html,
            'preview': preview, 'description': description}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_autocheck', renderer='json', xhr=True)
    @view_config(route_name='file_autosave', renderer='json', xhr=True)
    def auto_check(self):
        """Validate the current file, possibly save it, and continue."""
        storage = current_storage(self._request)[0]
        path, is_valid, fullname, opener, content = self._file_opener(storage)

        # Validate
        is_valid, new_content = opener.is_valid(
            self._request, storage, path, content, self._request.params)
        if not is_valid:
            errors = [self._request.localizer.translate(k)
                      for k in self._request.session.pop_flash('alert')]
            return {'error': '\n'.join(errors)}

        # Save?
        if '/autosave/' not in self._request.current_route_path():
            return None
        if not content:
            with open(fullname, "r") as hdl:
                content = hdl.read()
        if new_content != content:
            values = self._request.params.copy()
            if not values.get('message'):
                values['message'] = self._request.localizer.translate(
                    _('Automatic backup'))
            opener.save(self._request, storage, path, new_content, values)
            errors = [self._request.localizer.translate(k)
                      for k in self._request.session.pop_flash('alert')]
            return {'error': '\n'.join(errors)}
        return None

    # -------------------------------------------------------------------------
    @view_config(route_name='file_media', renderer='json', xhr=True)
    def media(self):
        """Return the URL of the searched media."""
        storage = current_storage(self._request)[0]
        name, opener = self._file_opener(storage)[2:4]
        media_id = self._request.params.get('id')
        name = opener.find_media(
            name, self._request.params.get('type'), media_id)
        if name is None:
            return {'src': ''}
        name = relpath(name, self._request.registry.settings['storage.root'])
        name = self._request.route_path(
            'file_download', storage_id=name.partition('/')[0],
            path=name.partition('/')[2])
        return {'src': name}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_resources_dirs', renderer='json', xhr=True)
    def resources_dirs(self):
        """Return the list of resource directories."""
        storage = current_storage(self._request)[0]
        storage_root = self._request.registry.settings['storage.root']
        name, opener = self._file_opener(storage)[2:4]
        dirs = opener.resources_dirs(name, self._request.params.get('type'))
        return {'dirs': [relpath(k, storage_root) for k in dirs]}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_resources_files', renderer='json', xhr=True)
    def resources_files(self):
        """Return the list of media files of a resource directory."""
        storage = current_storage(self._request)[0]
        name, opener = self._file_opener(storage)[2:4]
        path = self._request.params.get('path')
        if path[0:2] == './':
            path = join(dirname(name), path[2:])
        else:
            path = join(self._request.registry.settings['storage.root'], path)
        return {'files': opener.resources_files(
            path, self._request.params.get('type'),
            self._request.params.get('all') == 'false')}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_navigate', permission='stg.read')
    def navigate(self):
        """Display the next or previous file of the same type in the same
        directory.
        """
        storage = current_storage(self._request)[0]
        path, filename, fullname, opener = self._file_opener(storage)[0:4]
        if opener is None:
            return HTTPFound(self._request.route_path(
                'file_content', storage_id=storage['storage_id'], path=path))
        new_path = opener.navigate(
            dirname(fullname), filename, self._request.matchdict['direction'])
        if new_path:
            path = relpath(
                new_path, join(
                    self._request.registry.settings['storage.root'],
                    storage['storage_id']))
        else:
            self._request.session.flash(
                _("No more displayable file!"), 'alert')

        return HTTPFound(self._request.route_path(
            'file_render', storage_id=storage['storage_id'], path=path))

    # -------------------------------------------------------------------------
    @view_config(route_name='file_navigate_search', permission='stg.read')
    def navigate_search(self):
        """Display the next or previous file in the search results."""
        storage = current_storage(self._request)[0]
        path = '/'.join(self._request.matchdict['path'])
        files = 'search' in self._request.session \
            and self._request.session['search'].get('result') \
            and [(k['storage_id'], k['path'])
                 for k in self._request.session['search']['result']]
        if not files or (storage['storage_id'], path) not in files:
            return HTTPFound(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path=path))

        if self._request.matchdict['direction'] == 'next':
            files = files[files.index((storage['storage_id'], path)) + 1:]
        else:
            files = files[0:files.index((storage['storage_id'], path))]
            files.reverse()
        for item in files:
            fullname = join(
                self._request.registry.settings['storage.root'],
                item[0], item[1])
            if exists(fullname) and self._request.registry['opener']\
                    .get_opener(fullname, storage)[0]:
                return HTTPFound(self._request.route_path(
                    'file_render', storage_id=item[0], path=item[1]))

        self._request.session.flash(_("No more displayable file!"), 'alert')
        return HTTPFound(self._request.route_path(
            'file_render', storage_id=storage['storage_id'], path=path))

    # -------------------------------------------------------------------------
    @view_config(
        route_name='file_info', renderer='../Templates/fil_info.pt',
        permission='stg.read')
    def info(self):
        """Show file information and VCS log."""
        storage, handler = current_storage(self._request)
        path = self._request.matchdict['path']
        fullname = join(handler.vcs.path, *path).encode('utf8')
        filename = path[-1]
        path = '/'.join(path)
        if 'page_size' in self._request.params \
           and self._request.params['page_size'].strip():
            self._request.session['page_size'] = \
                int(self._request.params['page_size'])
        log = handler.vcs.log(
            dirname(path), filename,
            int(self._request.session.get('page_size', 20)))

        content = None
        action = get_action(self._request)[0]
        if action[0:4] == 'shw!':
            action = action[4:]
            content = handler.vcs.revision(fullname, action)
            if content is None:
                self._request.session.flash(
                    _('Unable to retrieve this revision:'
                      ' it was probably moved.'), 'alert')
            else:
                content = {
                    'route': 'file_revision',
                    'revision': action,
                    'file': self._highlight(fullname, content),
                    'label': action != '-' and _(
                        'Revision ${r}', {'r': action}) or ''}
        elif action[0:4] == 'dif!':
            action = action[4:]
            content = handler.vcs.diff(fullname, action)
            content = content.encode('utf8')
            content = {
                'route': 'file_diff',
                'revision': action,
                'file': self._highlight(fullname, content),
                'label': _('Differences with revision ${r}', {'r': action})}

        self._request.breadcrumbs.add(_('File information'))
        return {
            'storage': storage, 'path': path, 'dirpath': dirname(path),
            'filename': filename, 'mime_type': get_mime_type(fullname),
            'MIME_TYPES': MIME_TYPES, 'log': log, 'age': age,
            'has_lexer': self._has_lexer(fullname), 'content': content,
            'PAGE_SIZES': PAGE_SIZES}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_download', permission='stg.read')
    def download(self):
        """Download a file."""
        storage = current_storage(self._request)[0]
        path = self._request.matchdict['path']
        real_path = join(self._request.registry.settings['storage.root'],
                         storage['storage_id'], *path[0:-1])
        if not isdir(real_path):
            raise HTTPNotFound(comment=_('This file does not exist!'))
        return file_download(self._request, real_path, (path[-1],))

    # -------------------------------------------------------------------------
    @view_config(route_name='file_revision', permission='stg.read')
    def revision(self):
        """Retrieve a revision of a file."""
        handler, filename, fullname, revision = self._file_info()
        content = handler.vcs.revision(fullname, revision)

        if content is None:
            self._request.session.flash(
                _('Unable to retrieve this revision: it was probably moved.'),
                'alert')
            return HTTPFound(self._request.route_path(
                'file_info', storage_id=handler.uid,
                path='/'.join(self._request.matchdict['path'])))

        download_name = u'%s.r%s%s' % (
            splitext(filename)[0], revision, splitext(filename)[1])
        response = Response(content, content_type=get_mime_type(fullname)[0])
        response.headerlist.append((
            'Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # -------------------------------------------------------------------------
    @view_config(route_name='file_diff', permission='stg.read')
    def diff(self):
        """Differences between a version and current version."""
        handler, filename, fullname, revision = self._file_info()
        content = handler.vcs.diff(fullname, revision)

        download_name = u'%s.r%s.diff' % (splitext(filename)[0], revision)
        response = Response(content, content_type='text/x-diff')
        response.headerlist.append((
            'Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # -------------------------------------------------------------------------
    def _file_info(self):
        """Return handler, filename, fullname, and revision."""
        handler = current_storage(self._request)[1]
        path = self._request.matchdict['path']
        revision = self._request.matchdict['revision']
        fullname = handler.vcs.full_path(*path)
        if fullname is None or isdir(fullname):
            raise HTTPForbidden()

        return handler, path[-1], fullname, revision

    # -------------------------------------------------------------------------
    def _display_form(self):
        """Return form for display view.

        :return: (:class:`~..lib.form.Form` instance)
        """
        schema = SchemaNode(Mapping())
        if 'seed' in self._request.params:
            schema.add(SchemaNode(String(), name='seed'))
        if 'name' in self._request.params:
            schema.add(SchemaNode(
                String(), name='name', validator=Length(max=PATH_LEN)))
        if 'message' in self._request.params:
            schema.add(SchemaNode(
                String(), name='vcs_user',
                validator=Length(max=ID_LEN), missing=None))
            schema.add(SchemaNode(String(), name='vcs_password', missing=None))
            schema.add(SchemaNode(
                String(), name='message',
                validator=Length(max=DESCRIPTION_LEN), missing=None))
        form = Form(self._request, schema=schema)
        return form

    # -------------------------------------------------------------------------
    def _display_action(self, form, storage, handler, path, filename):
        """Return form and current action for display view.

        :param form: (:class:`~..lib.form.Form` instance)
            Current form.
        :param storage: (dictionary)
            Storage dictionary.
        :param handler: (:class:`~..lib.handler.Handler` instance)
            Storage Control System.
        :param path: (string)
            Relative path to the current file.
        :param filename: (string)
            Name of the current file.
        :return: (tuple)
            A tuple such as ``(action, items, working)``.
        """
        working = False
        action, items = get_action(self._request)
        save_vcs_user(self._request, storage)
        if action == 'upl!' and 'vcs_change' not in self._request.params:
            if storage['perm'] != 'writer':
                raise HTTPForbidden(
                    comment=_("You can't modify this storage!"))
            if not form.validate():
                action = '%s?' % action[0:3]
                return action, items, working
            upload_file = self._request.params.get('upload_file')
            if upload_file.filename != filename:
                self._request.session.flash(
                    _('File names are different.'), 'alert')
                action = '%s?' % action[0:3]
                return action, items, working
            handler = self._request.registry['handler'].get_handler(
                storage['storage_id'])
            translate = self._request.localizer.translate
            working = handler.launch(
                self._request, handler.upload,
                (vcs_user(self._request, storage),
                 path, [upload_file], filename,
                 form.values.get('message') or
                 translate(_('Uploading from disk'))))
        elif action[0:4] == 'npk!' and 'project' in self._request.session \
                and self._request.session['project']['perm'] \
                in ('leader', 'packmaker'):
            items = create_pack(
                self._request, (filename,), join(storage['storage_id'], path))
        elif action == 'dup!':
            if not form.validate():
                action = '%s?' % action[0:3]
                return action, items, working
            items = (form.values['name'],)
            if splitext(items[0])[1] != splitext(filename)[1]:
                items = ('%s%s' % (items[0], splitext(filename)[1]),)
            working = handler.launch(
                self._request, handler.duplicate,
                (vcs_user(self._request, storage), path, filename, items[0],
                 form.values.get(
                     'message',
                     self._request.localizer.translate(_('Duplication')))))

        return action, items, working

    # -------------------------------------------------------------------------
    def _file_opener(self, storage):
        """Return path, filename, fullname, opener and content.

        :param storage: (dictionary)
            Storage dictionary.
        :return: (tuple)
            A tuple such as ``(path, filename, fullname, opener, content)``.
        """
        path = self._request.matchdict['path']
        filename = path[-1] if path else ''
        fullname = join(self._request.registry.settings['storage.root'],
                        storage['storage_id'], *path)
        path = '/'.join(path)
        if not exists(fullname):
            raise HTTPNotFound(comment=_('This file does not exist!'))
        if isdir(fullname):
            return path, filename, None, None, None
        opener, content = \
            self._request.registry['opener'].get_opener(fullname, storage)
        return path, filename, fullname, opener, content

    # -------------------------------------------------------------------------
    def _search_scope(self):
        """Find eligible storage IDs and compute scope.

        :rtype: list
        :return:
            A list of tuples such as ``(storage_id, storage_label)``.
        """
        session = self._request.session
        route = self._request.route_path('storage_root', storage_id='')
        indexed_storages = [
            k[0] for k in DBSession.query(Storage.storage_id).filter(
                Storage.indexed_files != NULL)]

        scope = []
        storage_ids = []
        for item in session.get('menu', ''):
            for subitem in item[4] or ():
                if subitem[2] and subitem[2].startswith(route):
                    storage_id = subitem[2][len(route):]
                    if storage_id in indexed_storages:
                        scope.append((storage_id, subitem[0]))
                        storage_ids.append(storage_id)
                        self._request.registry['handler'].get_handler(
                            storage_id)

        if 'storage' in session and session['storage']['indexed'] \
                and session['storage']['storage_id'] not in storage_ids:
            scope.insert(
                0, (session['storage']['storage_id'],
                    session['storage']['label']))
            self._request.registry['handler'].get_handler(
                session['storage']['storage_id'])

        return scope

    # -------------------------------------------------------------------------
    def _search_filter(self, action):
        """Create the filter object for the search.

        :param str action:
            The possibly current action.
        :rtype: tuple
            A tuple like ``(wfilter, result_columns)`` where ``wfilter`` is a
           :class:`.lib.filter.Filter` object.
        """
        if 'search' in self._request.session:
            result_columns = self._request.session['search']['columns']
            inputs = self._request.session['search']['inputs']
        else:
            result_columns = [('score', 'score', _('Score'))]
            lang = self._request.session['lang']
            default_lang = self._request.registry.settings.get(
                'pyramid.default_locale_name', 'en')
            statics = []
            dynamics = []
            for indexer in DBSession.query(Indexer).order_by('result_column'):
                if indexer.result_column:
                    result_columns.append((
                        indexer.indexer_id, indexer.value_type,
                        indexer.label(lang, default_lang)))
                if indexer.display == 'hidden':
                    continue
                values = (indexer.value_type == 'boolean' and True) or \
                    (indexer.value_type in ('select', 'filetype') and
                     [('', u' ')]
                     + [(k.value, k.label) for k in indexer.values]) or None
                if indexer.display == 'static':
                    statics.append((
                        indexer.indexer_id, indexer.label(lang, default_lang),
                        True, values))
                else:
                    dynamics.append((
                        indexer.indexer_id, indexer.label(lang, default_lang),
                        False, values))
            inputs = sorted(statics + dynamics, key=lambda k: k[0])
            self._request.session['search'] = {
                'scope': [], 'inputs': inputs, 'columns': result_columns,
                'result': None}

        return Filter(
            self._request, 'search', inputs,
            remove=action[:4] == 'crm!' and action[4:] or None), result_columns

    # -------------------------------------------------------------------------
    def _search_form(self):
        """Return a search form.

        :rtype: :class:`~.lib.form.Form`
        """
        defaults = {}
        if self._request.session['search']['scope']:
            for storage_id in self._request.session['search']['scope']:
                defaults[u'~{0}'.format(storage_id)] = True
        elif 'storage' in self._request.session:
            defaults = {u'~{0}'.format(
                self._request.session['storage']['storage_id']): True}
        form = Form(self._request, defaults=defaults)
        form.forget('filter_value')
        return form

    # -------------------------------------------------------------------------
    def _search_execute(self, wfilter, values):
        """Search files in storages and return a result.

        :type  wfilter: :class:`.lib.filter.Filter`
        :param wfilter:
            The Whoosh filter to execute.
        :param dict values:
            Search form values.
        :rtype: list
        :return:
            A list of dictionaries each of them representing an answer.

        This method stores scope in ``session['search']['scope']`` and results
        in ``session['search']['result']``.
        """
        # Compute scope
        scope = []
        for storage_id in values:
            if storage_id[0] == '~' and values[storage_id]:
                scope.append(storage_id[1:])
                if storage_id == '~ALL~':
                    scope = ['ALL~']
                    break
        if not scope:
            self._request.session.flash(_('Select a storage!'), 'alert')
            return None
        self._request.session['search']['scope'] = scope
        if scope[0] == 'ALL~':
            scope = [k[0] for k in dbquery_storages(
                DBSession.query(Storage.storage_id),
                self._request.session['user_id'], True)]

        # Process filter in scope
        results = []
        fieldnames, wquery = wfilter.whoosh()
        for storage_id in scope:
            results += self._request.registry['handler'].search(
                storage_id, fieldnames, wquery)

        # Sort result
        sort = self._request.session['paging'][1]['search']['sort']
        results = sorted(
            results, key=lambda k: k.get(sort[1:], ''), reverse=sort[0] == '-')

        self._request.session['search']['result'] = results
        return results

    # -------------------------------------------------------------------------
    def _search_results(self, storage, path):
        """Results of search

        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the current file.
        :rtype: tuple or ``None``
        :return:
            A tuple such as ``(index, max)``
        """
        searches = 'search' in self._request.session \
            and self._request.session['search'].get('result') \
            and [(k['storage_id'], k['path'])
                 for k in self._request.session['search']['result']]
        searches = searches and (storage['storage_id'], path) in searches and (
            searches.index((storage['storage_id'], path)) + 1, len(searches))
        return searches

    # -------------------------------------------------------------------------
    @classmethod
    def _search_export_csv(
            cls, result, filenames, result_columns, download_name):
        """Return a Pyramid response containing a CSV file representing the
        result of search.

        :param list result:
            Search result.
        :param list filenames:
            List of files to include in the CSV file.
        :param list result_columns:
            Search result.
        :param str download_name:
            Visible name during download.
        :rtype: :class:`pyramid.response.FileResponse`
        """
        csv = CSV_DELIMITER.join([k[1] for k in result_columns]) + '\n'
        fields = [k[0] for k in result_columns]
        for item in result:
            if join(item['storage_id'], item['path']) in filenames:
                csv += CSV_DELIMITER.join([
                    k in item and u'{0}'.format(item[k]) or ''
                    for k in fields]) + '\n'
        response = Response(csv, content_type='text/csv')
        response.headerlist.append((
            'Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # -------------------------------------------------------------------------
    def _pop_read_write_routes(self, storage):
        """Remove from the bread crumbs.

        :param storage: (dictionary)
            Storage dictionary.
        """
        path = self._request.breadcrumbs.current_path()
        if path.startswith(self._request.route_path(
                'file_read', storage_id=storage['storage_id'], path='')) \
            or path.startswith(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path='')) \
            or path.startswith(self._request.route_path(
                'file_write', storage_id=storage['storage_id'], path='')) \
            or path.startswith(self._request.route_path(
                'file_edit', storage_id=storage['storage_id'], path='')):
            self._request.breadcrumbs.pop()

    # -------------------------------------------------------------------------
    @classmethod
    def _has_lexer(cls, fullname):
        """Return ``True`` if a lexer exists.

        :param fullname: (string)
            Full path to the file to display.
        :return: (boolean)
        """
        if fullname[-4:] in ('.rnc', '.rng'):
            return True
        try:
            get_lexer_for_filename(fullname)
        except ClassNotFound:
            return False
        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _highlight(cls, fullname, content):
        """Return a literal XHTML with syntax highlighting of the content.

        :param fullname: (string)
            Full path to the file to display.
        :param content: (string)
            Text to highlight.
        """
        try:
            content = content.decode('utf8')
        except UnicodeDecodeError:
            pass

        if fullname[-4:] == '.rnc':
            return literal('<div><pre>%s</pre></div>') % content
        elif fullname[-4:] == '.rng':
            return literal(highlight(content, XmlLexer(), HtmlFormatter()))
        return literal(highlight(
            content, get_lexer_for_filename(fullname), HtmlFormatter()))
