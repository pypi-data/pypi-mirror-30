# -*- coding: utf-8 -*-
"""These XML-RPC functions are called by Maestro client."""

from os import sep, walk
from os.path import join, exists, isfile, getmtime, getsize, dirname, relpath
from cStringIO import StringIO
import re
import zipfile
import xmlrpclib
from tempfile import NamedTemporaryFile

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from ..lib.i18n import _
from ..lib.utils import get_mime_type, camel_case, normalize_spaces
from ..lib.viewutils import connect_user, current_storage, dbquery_storages
from ..lib.viewutils import current_project, current_processing
from ..lib.packutils import pack_upload_content
from ..lib.xml import load_xml
from ..models import LABEL_LEN, DBSession
from ..models.storages import Storage
from ..models.indexers import Indexer
from ..models.projects import Project
from ..models.packs import Pack
from ..models.processings import Processing


# =============================================================================
def storages(request, context, with_index=True):
    """Return a list of available storages.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param with_index: (boolean, default=True)
        If ``True`` select only storages with indexed files.
    :return: (tuple)
        ``(error, result)``
    """
    # pylint: disable = E1103
    user = _user(request, context)
    if not user:
        return _not_authorized(request)

    result = [(k[0], k[1]) for k in dbquery_storages(
        DBSession.query(Storage.storage_id, Storage.label),
        user.user_id, with_index)]
    DBSession.close()
    return '', result


# =============================================================================
def indexes(request, context):
    """Return a list of available indexes.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :return: (tuple)
        ``(error, result)``
    """
    # pylint: disable = E1103
    user = _user(request, context)
    if not user:
        return _not_authorized(request)

    result = {}
    default_lang = request.registry.settings.get(
        'pyramid.default_locale_name', 'en')
    for indexer in DBSession.query(Indexer):
        if indexer.indexer_id != 'extract':
            values = [(k.value, k.label) for k in indexer.values] \
                if indexer.value_type == 'select' else None
            result[indexer.indexer_id] = (
                indexer.label(user.lang, default_lang), indexer.value_type,
                values and sorted(values, key=lambda k: k[1]) or '')
    DBSession.close()
    return '', result


# =============================================================================
def search(request, context, scope, query, limit):
    """Return the result of a search limited to ``limit`` lines.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :return: (tuple)
        ``(error, result)``
    """
    # pylint: disable = E1103
    user = _user(request, context)
    if not user:
        return _not_authorized(request)

    # Compute scope
    if not scope:
        DBSession.close()
        return request.localizer.translate(_('Storage is required!')), ''
    fullscope = [k[0] for k in dbquery_storages(
        DBSession.query(Storage.storage_id), user.user_id, True)]
    scope = fullscope if scope[0] == 'ALL' else (set(fullscope) & set(scope))
    if not scope:
        DBSession.close()
        return request.localizer.translate(_(
            'You cannot access this storage!')), ''

    # Compute fieldnames
    fieldnames = tuple(set([
        unicode(k.partition(':')[0].strip())
        for k in re.split('(AND|OR|NOT)', query) if ':' in k]))
    if len(fieldnames) < 1:
        DBSession.close()
        return request.localizer.translate(_('Field names are required!')), ''
    if len(fieldnames) == 1:
        query = query.replace('%s:' % fieldnames[0], '')

    # Process query in scope
    result = []
    query = unicode(query)
    for storage_id in scope:
        result += request.registry['handler'].search(
            storage_id, fieldnames, query, limit)

    # Cleanup and complete result
    result = sorted(result, key=lambda item: item[0], reverse=True)
    result = result[0:limit]
    root = request.registry.settings['storage.root']
    for item in result:
        item[1] = get_mime_type(join(root, item[2], item[3]))[1]
        if not item[4]:
            item[4] = ''
        if not item[5]:
            item[5] = ''

    DBSession.close()
    return '', result


# =============================================================================
def file_info(request, context, filename):
    """Return date and size of file ``filename``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param filename: (string)
        Relative path of file to search.
    :return: (tuple)
        ``(error, result)`` where result is a tuple like ``(file_mtime,
        file_size)``.
    """
    # pylint: disable = E1103
    user = _user(request, context)
    if not user:
        return _not_authorized(request)

    filename = _check_file(request, filename)
    if filename is None:
        return request.localizer.translate(_(
            'You cannot access this file!')), ''

    result = (getmtime(filename), getsize(filename))
    DBSession.close()
    return '', result


# =============================================================================
def file_download(request, context, filename):
    """Download file ``filename``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param filename: (string)
        Relative path of file to search.
    :return: (tuple)
        ``(error, result)``
    """
    # pylint: disable = E1103
    user = _user(request, context)
    if not user:
        return _not_authorized(request)

    filename = _check_file(request, filename)
    if filename is None:
        return request.localizer.translate(_(
            'You cannot access this file!')), ''

    with open(filename, 'rb') as hdl:
        result = xmlrpclib.Binary(hdl.read())

    DBSession.close()
    return '', result


# =============================================================================
def pack_info(request, context, content, project_label):
    """Return date and size of all files of a pack.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param content: (:class:`xmlrpclib.Binary` instance)
        Content of pack settings.
    :param project_label: (string)
        Label of the project to use.
    :return: (tuple)
        ``(error, result)`` where ``result`` is a tuple like ``(pack_exists,
        info_list)``. ``info_list`` is a list such as ``[(file_path,
        file_mtime, file_size),...]``.
    """
    # pylint: disable = too-many-locals
    # Find project
    project = _find_project(request, context, project_label)
    if isinstance(project, basestring):
        return project, ''

    # Load pack settings
    pack_doc = load_xml(
        'pack.xml',
        {'publiforge':
         join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')},
        content.data)
    if isinstance(pack_doc, basestring):
        return pack_doc, ''

    # Does pack exists?
    # pylint: disable = E1103
    known = normalize_spaces(pack_doc.findtext('pack/label'), LABEL_LEN)
    known = bool(DBSession.query(Pack.pack_id).filter_by(
        project_id=project['project_id'], label=known).first())
    DBSession.close()

    # Browse files
    root = request.registry.settings['storage.root']
    done = set()
    info_list = list()
    for filename in pack_doc.xpath(
            'pack/files/file|pack/resources/resource|pack/templates/template'):
        filename = filename.text.strip()
        fullname = join(root, filename)
        if filename in done or not exists(fullname):
            continue
        done.add(filename)
        if isfile(fullname):
            info_list.append((filename, getmtime(fullname), getsize(fullname)))
            continue
        for path, ignored_, files in walk(fullname):
            for name in files:
                fullname = join(path, name)
                name = relpath(fullname, root)
                if name not in done:
                    done.add(name)
                    info_list.append((
                        name, getmtime(fullname), getsize(fullname)))

    return '', (known, info_list)


# =============================================================================
def pack_upload(request, context, content, project_label, message):
    """Upload a pack inot the project ``project``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param content: (:class:`xmlrpclib.Binary` instance)
        Content of the pack.
    :param project_label: (string)
        Label of the project to use.
    :param message: (string)
        Message for commit operation.
    :return: (tuple)
        ``(error, result)``
    """
    # Find project
    project = _find_project(request, context, project_label)
    if isinstance(project, basestring):
        return project, ''

    # Save pack content
    error = pack_upload_content(
        request, project['project_id'], message, '', StringIO(content.data))

    DBSession.close()
    return error and request.localizer.translate(error) or '', ''


# =============================================================================
def build(request, context, project_label, pack_label, processing_label):
    """Upload a pack inot the project ``project``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param project_label: (string)
        Label of the project to use.
    :param pack_label: (string)
        Label of the pack to use.
    :param processing_label: (string)
        Label of the processing to use.
    :return: (tuple)
        ``(error, result)``
    """
    # Find project
    project = _find_project(request, context, project_label)
    if isinstance(project, basestring):
        return project, ''

    # Find pack
    pack = DBSession.query(Pack).filter_by(
        project_id=project['project_id'], label=pack_label).first()
    if not pack:
        DBSession.close()
        return request.localizer.translate(_('Incorrect pack!')), ''

    # Find processing
    processing = DBSession.query(Processing.processing_id)\
        .filter_by(project_id=project['project_id'], label=processing_label)\
        .first()
    if not processing:
        DBSession.close()
        return request.localizer.translate(_('Incorrect processing!')), ''
    processing, processor = current_processing(
        request, project['project_id'], processing[0])[0:2]
    if processing.processor.startswith('Parallel'):
        DBSession.close()
        return request.localizer.translate(_(
            'Parallel processing is forbidden!')), ''

    # Launch build
    front_build = request.registry['fbuild'].start_build(
        request, processing, processor, pack)
    if not front_build:
        DBSession.close()
        return request.localizer.translate(_(
            request.session.pop_flash('alert'))), ''

    DBSession.close()
    return '', ''


# =============================================================================
def build_log(request, context, build_id):
    """Send log of build ``build_id``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param build_id: (string)
        ID of build to retrieve.
    :return: (tuple)
        ``(error, result)``
    """
    user = _user(request, context)
    if not user:
        return _not_authorized(request)

    # Check build ID
    result = request.registry['fbuild'].result(build_id)
    if not result or not result.get('log'):
        DBSession.close()
        return request.localizer.translate(_('No log to download!')), ''
    log = '\n'.join(['[%-7s] %s' % (k[1], k[3]) for k in result['log']])
    DBSession.close()
    return '', log


# =============================================================================
def results(request, context, project_label):
    """Upload a pack inot the project ``project``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param project_label: (string)
        Label of the project to use.
    :return: (tuple)
        ``(error, (working, results))``
    """
    # Find project
    project = _find_project(request, context, project_label)
    if isinstance(project, basestring):
        return project, (False, [])

    # Build list
    build_list = request.registry['fbuild'].build_list(
        project['project_id'], request.session['user_id'])[:]
    if not build_list:
        DBSession.close()
        return '', (False, [])

    # Pack labels
    packs = [k['pack_id'] for k in build_list]
    packs = dict(DBSession.query(Pack.pack_id, Pack.label)
                 .filter_by(project_id=project['project_id'])
                 .filter(Pack.pack_id.in_(packs)).all())
    build_list = [k for k in build_list if k['pack_id'] in packs]
    if not build_list:
        DBSession.close()
        return '', (False, [])

    # Processing labels
    processings = [k['processing_id'] for k in build_list]
    processings = dict(
        DBSession.query(Processing.processing_id, Processing.label)
        .filter_by(project_id=project['project_id'])
        .filter(Processing.processing_id.in_(processings)).all())

    # Progress
    working, progress = request.registry['fbuild'].progress(
        request, [k['build_id'] for k in build_list])

    # Complete result list
    for k, result in enumerate(build_list):
        build_list[k]['processing'] = processings.get(
            result['processing_id'],
            request.localizer.translate(_(u'Deleted processing…')))
        build_list[k]['pack'] = packs[result['pack_id']]
        if result['build_id'] in progress:
            build_list[k]['progress'] = progress[result['build_id']][1]
        del build_list[k]['processing_id']
        del build_list[k]['pack_id']
        del build_list[k]['user_id']
        if 'files' in result:
            del build_list[k]['files']

    DBSession.close()
    return '', (working, build_list)


# =============================================================================
def result_download(request, context, build_id):
    """Download result of build ``build_id``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param build_id: (string)
        ID of build to retrieve.
    :return: (tuple)
        ``(error, result)``
    """
    user = _user(request, context)
    if not user:
        return _not_authorized(request)

    # Check build ID
    result = request.registry['fbuild'].result(build_id)
    if not result or not result.get('files'):
        DBSession.close()
        return request.localizer.translate(
            _('No result to download!')), ''

    # Find output
    project_id, processing_id = build_id.split('-')[0:2]
    output = DBSession.query(Processing.output).filter_by(
        project_id=project_id, processing_id=processing_id).first()
    if not output:
        DBSession.close()
        return request.localizer.translate(
            _('This processing does not exist!')), ''
    output = output[0].replace(
        '%(user)s', camel_case(request.session['login']))
    DBSession.close()

    # Single file
    storage_root = request.registry.settings['storage.root']
    fullname = join(storage_root, output, result['files'][0])
    if len(result['files']) == 1 and isfile(fullname):
        with open(fullname) as hdl:
            content = hdl.read()
        return '', (result['files'][0], xmlrpclib.Binary(content))

    # Several files
    tmp = NamedTemporaryFile(
        dir=request.registry.settings['temporary_dir'])
    zip_file = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name in result['files']:
        fullname = join(storage_root, output, name)
        if isfile(fullname):
            zip_file.write(fullname, name)
    zip_file.close()
    with open(tmp.name) as hdl:
        content = hdl.read()

    return '', ('build_%s.zip' % build_id, xmlrpclib.Binary(content))


# =============================================================================
def _user(request, context):
    """Check if the user exists and the request is authorized.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A dictionary with keys ``login``, ``password``.
    :return: (boolean)
        ``True`` if authorized.
    """
    # pylint: disable = E1103, W0212
    user = connect_user(request, context['login'], context['password'])
    if not isinstance(user, int):
        user.setup_environment(request)
        request.locale_name = request.session['lang']
        return user
    return None


# =============================================================================
def _not_authorized(request):
    """Return ``('Not authozied!', '')`` where error message is translated.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :return: (tuple)
    """
    DBSession.close()
    return request.localizer.translate(_('Not authorized!')), ''


# =============================================================================
def _check_file(request, filename):
    """Check if file ``filename`` exists and if user is authorized to get it.

    :param filename: (string)
        Relative path to file.
    :return: (string or ``None``)
        Absolute path to file.
    """
    # Check access to storage
    storage_id = filename.partition(sep)[0]
    try:
        current_storage(request, storage_id)
    except (HTTPNotFound, HTTPForbidden):
        DBSession.close()
        return None

    # Check access to file
    filename = join(request.registry.settings['storage.root'], filename)
    if not isfile(filename):
        DBSession.close()
        return None

    return filename


# =============================================================================
def _find_project(request, context, project_label):
    """Find the project according to its label.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        A context for authentication.
    :param project_label: (string)
        Label of the project to use.
    :return: (dictionary or string)
        Project dictionary or error string.
    """
    # Check user
    user = _user(request, context)
    if not user:
        return _not_authorized(request)[0]

    # Check project
    project = DBSession.query(Project).filter_by(
        label=project_label).first()
    if not project:
        DBSession.close()
        return request.localizer.translate(_('Incorrect project!'))
    try:
        project = current_project(request, project.project_id)
    except (HTTPNotFound, HTTPForbidden):
        DBSession.close()
        return request.localizer.translate(_(
            'You cannot access this project!'))
    return project
