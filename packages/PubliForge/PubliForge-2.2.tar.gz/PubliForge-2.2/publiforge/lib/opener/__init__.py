"""A file *opener* is a class to display, render and edit some specific
kind of file."""
# pylint: disable = no-name-in-module

from logging import getLogger
from os import listdir, makedirs
from os.path import join, exists, dirname, isfile, normpath
from os.path import sep, splitext
from locale import getdefaultlocale
from shutil import rmtree, copy
from ConfigParser import ConfigParser
from fnmatch import fnmatch
from collections import OrderedDict
from cgi import escape
import re

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.lexers import XmlLexer
from pygments.util import ClassNotFound
from pygments.formatters import HtmlFormatter
from webhelpers2.html import literal
from colander import SchemaNode, Mapping, String, Length
from lxml import etree

from pyramid.asset import abspath_from_asset_spec

from ..i18n import _, localizer
from ..config import settings_get_list
from ..utils import copy_content, decrypt, normalize_spaces
from ..viewutils import variable_schema_node
from ..form import Form
from ..xml import load_xml, local_text
from ..viewutils import current_storage
from ...models import ID_LEN, DBSession
from ...models.storages import StorageUser


LOG = getLogger(__name__)
PYGMENT_CSS = '/Static/Css/pygments.css'
PYGMENT_MAX_SIZE = 8388608
CODEMIRROR_MAX_SIZE = 2097152
CODEMIRROR = '/Static/Js/codemirror.js'
CODEMIRROR_LOADER = '/Static/Js/codemirror_loader.js'
CODEMIRROR_CSS = '/Static/Css/codemirror.css'
CODEMIRROR_CLASS = 'editor'
MAIN_ROUTE = '/Static'
OPENER_ROUTE = 'file/opener/%s'
OPENER_DEFAULTS = [
    'ImageEdit', 'Image', 'Publiset', 'Xml', 'Ini', 'Plain', 'NoMore']


# =============================================================================
class OpenerManager(object):
    """This class manages file openers.

    :param dict settings:
        Setting dictionary.

    One instance of :class:`OpenerManager` is created during application
    initialization. It is only used in front mode. It is stored in application
    registry.

    ``self._openers`` is a 'sorted by preference' list of available file
    openers.
    """

    # -------------------------------------------------------------------------
    def __init__(self, settings):
        """Constructor method."""
        # Empty cache directory
        self.settings = settings
        if not settings.get('opener.cache'):
            exit('*** Must define a cache directory for openers.')
            return
        if not exists(settings['opener.cache']):
            makedirs(settings['opener.cache'])

        # Read all available openers
        roots = settings_get_list(settings, 'opener.roots')
        roots.append(join(dirname(__file__), '..', '..', 'Openers'))
        self.opener_roots = {}
        for root in roots:
            root = normpath(abspath_from_asset_spec(root))
            if not exists(root):
                continue
            for opener_id in listdir(root):
                if opener_id not in self.opener_roots and \
                   exists(join(root, opener_id, 'opener.xml')):
                    self.opener_roots[opener_id] = join(root, opener_id)

        # Create listed openers
        activated = settings_get_list(settings, 'opener.list') \
            + OPENER_DEFAULTS
        self._openers = OrderedDict()
        for pattern in activated:
            for opener_id in sorted(self.opener_roots, reverse=True):
                if opener_id not in self._openers \
                   and fnmatch(opener_id, pattern):
                    self._load_opener(opener_id)

    # -------------------------------------------------------------------------
    def ids(self):
        """Return a list of IDs of available openers.

        :rtype: list
        """
        return self._openers.keys()

    # -------------------------------------------------------------------------
    def add_static_views(self, configurator):
        """Possibly, add static view for openers.

        :type  configurator: :class:`pyramid.config.Configurator`
        :param configurator:
            Object to configure a Pyramid application registry.
        """
        done = set()
        for opener_id in self._openers:
            route, path = self._openers[opener_id].route()
            if route is not None and route not in done:
                configurator.add_static_view(route, path, cache_max_age=3600)
                done.add(route)

    # -------------------------------------------------------------------------
    def get_opener(self, filename, storage):
        """Find the best opener for file ``filename``.

        :param str filename:
            Full path to file to check.
        :param dict storage:
            Storage dictionary.
        :rtype: tuple
        :return:
            A tuple such as ``(opener, content)`` where ``opener`` is not
            ``None`` if an opener matches.
        """
        content = None
        done = set()
        for opener_id in storage['openers'] + self._openers.keys():
            if opener_id in done:
                continue
            if opener_id == 'NoMore':
                return None, content
            if opener_id in self._openers:
                match, content = self._openers[opener_id].match(
                    filename, content)
                if match:
                    return self._openers[opener_id], content
            done.add(opener_id)
        return None, content

    # -------------------------------------------------------------------------
    def descriptions(self, request, opener_ids=None):
        """Return a dictionary of tuples such as ``(label, description)`` for
        each opener of ``opener_ids`` list.

        :type  request: :class:`pyramid.request.Request`
        :param request: (optional)
            Current request.
        :param opener_ids: (dicrionary, optional)
            List of IDs of opener to check. If ``None``, return the
            descriptions of all openers.
        :return: (list)
        """
        infos = OrderedDict()
        if opener_ids is None:
            opener_ids = self._openers.keys()
        for opener_id in opener_ids:
            if opener_id in self._openers:
                infos[opener_id] = (
                    self._openers[opener_id].label(request),
                    self._openers[opener_id].description(request))
        return infos

    # -------------------------------------------------------------------------
    def has_seeds(self, opener_ids):
        """Return ``True`` if at least one opener among ``openers`` has a seed.

        :param opener_ids: (list)
            List of IDs of opener to check.
        :return: (boolean)
        """
        for opener_id in opener_ids:
            if opener_id in self._openers \
               and self._openers[opener_id].has_seeds():
                return True

        return False

    # -------------------------------------------------------------------------
    def seed_list(self, request, opener_ids):
        """Return a list of couples such as ``(seed_file, seed_label)``.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param opener_ids: (list)
            List of IDs of opener to use.
        :return: (list)
        """
        seeds = []
        for opener_id in opener_ids:
            if opener_id in self._openers:
                seeds += self._openers[opener_id].seed_list(request)

        return tuple(sorted(seeds, key=lambda k: k[1]))

    # -------------------------------------------------------------------------
    def seed_fullpath(self, request, path):
        """Install the environment and return the absolute path to the seed
        file.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param path: (string)
            Relative path to the seed.
        :return: (string or ``None``)
        """
        opener_id = path.split(sep)[0]
        if opener_id not in self._openers:
            request.session.flash(
                _('Unknown opener "${o}"', {'o': opener_id}), 'alert')
            return None
        self._openers[opener_id].install_environment(request)
        return join(self.settings['opener.cache'], path)

    # -------------------------------------------------------------------------
    def _load_opener(self, opener_id):
        """Return the opener which ID is ``opener_id``.

        :param opener_id: (string)
            ID of the opener to load.
        :return: (opener class or ``none``)
        """
        # Load XML file
        opener_xml = load_xml(
            join(self.opener_roots[opener_id], 'opener.xml'),
            {'publiforge':
             join(dirname(__file__), '..', '..', 'RelaxNG', 'publiforge.rng')})
        if isinstance(opener_xml, basestring):
            LOG.error(
                'Opener "%s": %s', opener_id,
                localizer(getdefaultlocale()[0]).translate(opener_xml))
            return

        # Load module
        # pylint: disable = maybe-no-member
        module_name = opener_xml.findtext('opener/module').strip()
        try:
            module = __import__(module_name, fromlist=['Opener'])
        except ImportError as error:
            LOG.error('Opener "%s": %s', opener_id, error)
            return
        self._openers[opener_id] = module.Opener(self, opener_id, opener_xml)


# =============================================================================
class Opener(object):
    """Base class for file opener class.

    :type  opener_manager: :class:`OpenerManager`
    :param opener_manager:
        Application :class:`OpenerManager` object.
    :param str opener_id:
        ID of this opener.
    :type  opener_xml: :class:`lxml.etree.ElementTree`
    :param opener_xml:
        ID of this opener.
    """
    # pylint: disable = too-many-public-methods

    _config_file = None

    # -------------------------------------------------------------------------
    def __init__(self, opener_manager, opener_id, opener_xml):
        """Constructor method."""
        self.opener_id = opener_id
        self._manager = opener_manager
        self._path = join(opener_manager.settings['opener.cache'], opener_id)
        self._opener_xml = opener_xml
        self._config = None
        self._variables_xml = None

    # -------------------------------------------------------------------------
    def label(self, request=None):
        """Label in local or default language.

        :type  request: :class:`pyramid.request.Request`
        :param request: (optional)
            Current request.
        """
        return local_text(
            self._opener_xml, 'opener/label', request,
            lang=None if request is not None else 'en', default=self.opener_id)

    # -------------------------------------------------------------------------
    def description(self, request=None):
        """Description in local or default language.

        :type  request: :class:`pyramid.request.Request`
        :param request: (optional)
            Current request.
        """
        return local_text(
            self._opener_xml, 'opener/description', request,
            lang=None if request is not None else 'en').replace(' --', '<br/>')

    # -------------------------------------------------------------------------
    def information(self, request, name):
        """Return a description of object ``name`` in local or default
        language.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param name: (string)
            Name of the variable on which we are looking for information.
        :return: (string or ``None``)
        """
        # pylint: disable = maybe-no-member
        if not self.install_environment(request) \
           or not self._load_variables_xml():
            return None

        var = self._variables_xml.xpath(
            'variables/group[@name="%s"]/var[@name="%s"]'
            % (name.partition(':')[0], name.partition(':')[2]))
        if var:
            return literal('<b>%s</b><br/>%s' % (
                local_text(var[0], 'label', request),
                local_text(var[0], 'description', request).replace(
                    ' --', '<br/>')))
        return None

    # -------------------------------------------------------------------------
    def has_seeds(self):
        """Return ``True`` if at least one seed exists.

        :rtype: bool
        """
        return self._opener_xml.find('opener/seeds') is not None

    # -------------------------------------------------------------------------
    def seed_list(self, request):
        """Return a list of couples such as ``(seed_file, seed_label)`` where
        ``seed_file`` is a relative path to the seed file and ``seed_label`` a
        localized label.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :rtype: list
        """
        seeds = []
        root = self._opener_xml.find('opener/seeds')
        if root is None:
            return seeds
        for elt in root:
            if elt.findtext('file'):
                seeds.append((
                    join(self.opener_id, elt.findtext('file')),
                    local_text(elt, 'label', request)))
        return seeds

    # -------------------------------------------------------------------------
    def match(self, fullname, content=None):
        """Check whether this opener matches with the file ``fullname``.

        :param str fullname:
            Full path to file to check.
        :param str content: (optional)
            Content of the file to check.
        :rtype: tuple
        :return:
            A tuple such as ``(match, content)`` where ``match`` is ``True``
            if the opener matches.
        """
        # Without configuration file
        if self._config_file is None:
            if fullname[-4:] in ('.rnc', '.rng'):
                return True, content
            try:
                get_lexer_for_filename(fullname)
            except (ClassNotFound, KeyError):
                return False, content
            return True, content

        # With configuration file
        self.install_environment()
        regex1 = self._config_get('Match', 'file_regex')
        if regex1 and not re.search(regex1, fullname):
            return False, content

        regex2 = self._config_get('Match', 'content_regex')
        if not regex2:
            return bool(regex1), content
        if content is None:
            with open(fullname, 'r') as hdl:
                content = hdl.read()
        return bool(re.search(regex2, content)), content

    # -------------------------------------------------------------------------
    def read(self, request, storage, path, content=None):
        """Literal XHTML to display the file content.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the file to read.
        :param str content: (optional)
            Content of the file to read.
        :rtype: str
        :return:
            A piece of literal XHTML code.
        """
        if not self.install_environment(request, can_reset=True):
            return ''

        content = self._load_content(request, storage, path, content)
        fullname = join(
            request.registry.settings['storage.root'], storage['storage_id'],
            path)

        if fullname[-4:] == '.rnc' or len(content) > PYGMENT_MAX_SIZE:
            return literal('<div><pre>%s</pre></div>') % content
        if fullname[-4:] == '.rng':
            return literal(highlight(content, XmlLexer(), HtmlFormatter()))
        return literal(highlight(
            content, get_lexer_for_filename(fullname), HtmlFormatter()))

    # -------------------------------------------------------------------------
    def title(self, request, storage, path, content=None):
        """Return a title for the current file.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the native file.
        :param str content: (optional)
            Initial content of the file to edit.
        :rtype: :class:`str` or ``None``
        :return:
            A piece of XHTML representing the title of the file.
        """
        pass

    # -------------------------------------------------------------------------
    def overview(self, request, storage, path, content=None):
        """Return an overview for the current file.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the native file.
        :param str content: (optional)
            Initial content of the file to edit.
        :rtype: :class:`str` or ``None``
        :return:
            A piece of XHTML representing the file.
        """
        if splitext(path)[1] in ('.eps', '.ps'):
            return None
        if not self.install_environment(request):
            return None
        content = self._load_content(request, storage, path, content)
        if content is None:
            return None
        html = ''
        for count, line in enumerate(content[0:1024].split('\n')):
            html += '<div>%s</div>' % escape(line[0:96])
            if count > 4:
                break
        return html

    # -------------------------------------------------------------------------
    @classmethod
    def can_render(cls):
        """Return ``True`` if it can produce a rendering.

        :rtype: bool
        """
        return False

    # -------------------------------------------------------------------------
    @classmethod
    def render(cls, request, storage, path, content=None, native=None):
        """Literal XHTML to display file rendering.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the file to render.
        :param str content: (optional)
            Content of the file to render.
        :rtype: native object
        :param native: (optional)
            Object to convert.
        :rtype: str
        :return:
            A piece of literal XHTML code.
        """
        # pylint: disable = unused-argument
        return ''

    # -------------------------------------------------------------------------
    @classmethod
    def can_write(cls):
        """Return ``True`` if it can simply modify the file.

        :rtype: bool
        """
        return True

    # -------------------------------------------------------------------------
    def write(self, request, storage, path, content=None):
        """XHTML form and content for the file to write.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the file to write.
        :param str content: (optional)
            Content of the file to write.
        :rtype: tuple
        :return:
            A tuple such as ``(form, literal_html, content)`` where ``content``
            is the current state of the content.
        """
        schema = self._vcs_schema(storage)
        schema.add(SchemaNode(String(), name='code'))
        form = Form(request, schema=schema)

        if not self.install_environment(request, can_reset=True):
            return form, '', content
        content = self._get_content(
            request, storage, path, content, request.params)[0]
        if content is None:
            return form, '', content
        if not content or len(content) > CODEMIRROR_MAX_SIZE:
            request.session.flash(
                _("This file can't be edited online."), 'alert')
            return form, '', content

        try:
            content = content.decode('utf8')
        except UnicodeEncodeError:
            pass
        textarea = form.textarea(
            'code', content, rows=30, cols=80, class_=CODEMIRROR_CLASS)
        if self._config_file is not None and \
           self._config_get('Write', 'auto.check'):
            textarea = form.textarea(
                'code', content, rows=30, cols=80, class_=CODEMIRROR_CLASS,
                data_autocheck=self._config_get('Write', 'auto.check'))
        else:
            textarea = form.textarea(
                'code', content, rows=30, cols=80, class_=CODEMIRROR_CLASS)
        return form, textarea, content.encode('utf8')

    # -------------------------------------------------------------------------
    @classmethod
    def can_edit(cls):
        """Return ``True`` if it can produce an editor.

        :rtype: bool
        """
        return False

    # -------------------------------------------------------------------------
    @classmethod
    def edit(cls, request, action, storage, path, content=None):
        """XHTML form and content for the file to edit.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param str action: ('sav!', 'wrt!' or 'edt!')
            Current action
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the file to edit.
        :param str content: (optional)
            Content of the file to edit.
        :rtype: :class:`~.form.Form` or :class:`str`
        :return:
            A tuple such as ``(form, literal_html, native)`` where ``native``
            is the current state of the file.
        """
        # pylint: disable = unused-argument
        return Form(request), '', None

    # -------------------------------------------------------------------------
    @classmethod
    def find_media(cls, filename, media_type, media_id, patterns=None,
                   extensions=None):
        """Return the absolute path to the media ``media_id``.

        :param filename: (string)
            Full path to file being processed.
        :param media_type: ('image', 'audio' or 'video')
            Media type.
        :param media_id: (string)
            Media ID.
        :param patterns: (list, optional)
            List of patterns to check.
        :param extensions: (list, optional)
            List of extensions to check.
        :return: (string)
            URL media file or ``None``.
        """
        # pylint: disable = unused-argument
        return

    # -------------------------------------------------------------------------
    @classmethod
    def resources_dirs(cls, filename, media_type):
        """Return the list of resource directories.

        :param filename: (string)
            Full path to file being processed.
        :param media_type: ('image', 'audio' or 'video')
            Media type.
        :return: (list)
        """
        # pylint: disable = unused-argument
        return []

    # -------------------------------------------------------------------------
    @classmethod
    def resources_files(cls, path, media_type, media_only):
        """Return the list of media files of ``path`` directory.

        :param path: (string)
            Full path to the directory to browse.
        :param media_type: ('image', 'audio' or 'video')
            Media type.
        :param media_only: (boolean)
            If ``True``, return files following the media extension only.
        :return: (list)
        """
        # pylint: disable = unused-argument
        return []

    # -------------------------------------------------------------------------
    def save(self, request, storage, path, content, values):
        """Reconstitute and save the current file.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the file to save.
        :param str content:
            Initial value of content.
        :param dict values:
            Form values.
        :rtype: bool
        """
        # Check validity
        if request.session.peek_flash('alert'):
            return False
        is_valid, content = self.is_valid(
            request, storage, path, content, values)
        if not is_valid:
            return False

        # Get storage handler
        handler, user = self._storage_handler(request, storage)
        if handler is None:
            return False

        # Replace file
        handler.replace(
            user, path, content,
            values.get('message') or
            request.localizer.translate(_('On-line editing')))
        if handler.progress()[0] == 'error':
            request.session.flash(handler.progress()[1], 'alert')
            return False
        handler.cache.clear()

        return True

    # -------------------------------------------------------------------------
    def is_valid(self, request, storage, path, content=None, values=None):
        """Check whether the content is valid.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the native file.
        :param str content: (optional)
            Content of the file.
        :param dict values: (optional)
            Form values or request POST parameters.
        :rtype: tuple
        :return:
            A tuple such as ``(is_valid, content)``.
        """
        if not self.install_environment(request):
            return False, None
        content, trust = self._get_content(
            request, storage, path, content, values)
        if trust is True and bool(content):
            return True, content
        if trust is False or not bool(content):
            return False, content
        return self._content2native(request, content) is not None, content

    # -------------------------------------------------------------------------
    def css(self, mode, request=None):
        """Return a list of CSS files for the mode ``mode``.

        :param mode: (``'read'``, ``'render'``, ``'write'`` or ``'edit'``)
            Current mode for CSS.
        :param request: (:class:`pyramid.request.Request` instance, optional)
            Current request.
        :return: (tuple)
        """
        # Without configuration file
        if self._config_file is None:
            if mode == 'read':
                return (PYGMENT_CSS,)
            if mode == 'write':
                return (CODEMIRROR_CSS,)
            return tuple()

        # With configuration file
        lang = request.session['lang'] if request else 'en'
        routes = self._config_get(mode.capitalize(), 'css')
        return[k.strip().format(lang=lang) for k in routes.split(',')] \
            if routes else ()

    # -------------------------------------------------------------------------
    def javascript(self, mode, request=None):
        """Return list of JavaScript files for the mode ``mode``.

        :param mode: (``'read'``, ``'render'``, ``'write'`` or ``'edit'``)
            Current mode for CSS.
        :param request: (:class:`pyramid.request.Request` instance, optional)
            Current request.
        :return: (tuple)
        """
        # Without configuration file
        if self._config_file is None:
            if mode == 'write':
                return (CODEMIRROR, CODEMIRROR_LOADER)
            return tuple()

        # With configuration file
        lang = request.session['lang'] if request else 'en'
        routes = self._config_get(mode.capitalize(), 'javascript')
        return [k.strip().format(lang=lang) for k in routes.split(',')] \
            if routes else ()

    # -------------------------------------------------------------------------
    def position(self, directory, filename):
        """Return the number of files of the same type and the position of the
        current file.

        :param directory: (string)
            Full path to the directory containing the current file.
        :param filename: (string)
            Name of the current file.
        :return: (tuple)
            A tuple such as ``(position, count)``.
        """
        files = sorted(listdir(directory))
        count = 0
        position = 0
        for name in files:
            if filename == name:
                position = count
            name = join(directory, name)
            if isfile(name) and self.match(name)[0]:
                count += 1
        return position + 1, count

    # -------------------------------------------------------------------------
    def navigate(self, directory, filename, direction):
        """Return the next or previous file of the same type.

        :param directory: (string)
            Full path to the directory containing the current file.
        :param filename: (string)
            Name of the current file.
        :param direction: (``'previous'`` or ``'next'``)
            Direction of the navigation.
        :return: (string)
            Full path to next (or previous) file or ``None``.
        """
        files = sorted(listdir(directory))
        if direction == 'next':
            files = files[files.index(filename) + 1:]
        else:
            files = files[0:files.index(filename)]
            files.reverse()
        for name in files:
            name = join(directory, name)
            if isfile(name) and self.match(name)[0]:
                return name
        return None

    # -------------------------------------------------------------------------
    def route(self):
        """Return a route path and a full path to a directory for static data.

        :return: (tuple)
            A tuple such as ``(route_path, directory_path)`` or
            ``(None, None)``.
        """
        public = self._opener_xml.findtext('opener/public')
        if public is None:
            return None, None
        return OPENER_ROUTE % self.opener_id, join(self._path, public.strip())

    # -------------------------------------------------------------------------
    def install_environment(  # noqa
            self, request=None, opener_id=None, target=None, can_reset=False):
        """Install the opener directory, possibly with inheritance, in the
        opener cache directory.

        :param request: (:class:`pyramid.request.Request` instance, optional)
            Current request.
        :param opener_id: (string, optional)
            ID of the opener to install, by default the object itself.
        :param target: (string, optional)
            Full path to the target directory.
        :param can_reset: (boolean, default=False)
            If ``can_reset`` is ``True`` and ``opener.develop`` is ``'true'``
            in settings, the opener is destroyed and created again.
        :return: (boolean)
        """
        # Check situation
        # pylint: disable = too-many-branches
        opener_id = opener_id or self.opener_id
        if opener_id not in self._manager.opener_roots:
            if request is not None:
                request.session.flash(
                    _('Opener "${o}" is missing.', {'o': opener_id}), 'alert')
            return False
        if target is None:
            target = self._path
            if can_reset \
               and self._manager.settings.get('opener.develop') == 'true' \
               and exists(target):
                rmtree(target)
                self._config = None
                self._variables_xml = None
            if exists(target):
                return True
        try:
            makedirs(target)
        except OSError:
            pass

        # Read opener.xml file to check if other openers are needed
        tree = etree.parse(
            join(self._manager.opener_roots[opener_id], 'opener.xml'))
        for elt in tree.findall('opener/ancestors/ancestor'):
            if not self.install_environment(request, elt.text.strip(), target):
                if exists(target):
                    rmtree(target)
                self._config = None
                self._variables_xml = None
                return False

        # Install opener
        for elt in tree.findall('opener/imports/import'):
            source = elt.text.strip()
            source = abspath_from_asset_spec(elt.text.strip()) \
                if ':' in source \
                else join(self._manager.opener_roots[opener_id], source)
            if not exists(source):
                if request is not None:
                    request.session.flash(_(
                        'Opener "${o}" calls a missing file: "${s}".',
                        {'o': opener_id, 's': normpath(source)}), 'alert')
                if exists(target):
                    rmtree(target)
                self._config = None
                self._variables_xml = None
                return False
            if isfile(source):
                if not exists(dirname(join(target, elt.get('to')))):
                    makedirs(dirname(join(target, elt.get('to'))))
                copy(source, join(target, elt.get('to')))
            else:
                copy_content(source, join(target, elt.get('to')), force=True)
        copy_content(self._manager.opener_roots[opener_id], target, force=True)
        return True

    # -------------------------------------------------------------------------
    def _get_content(self, request, storage, path, content=None, values=None):
        """Get from the request or from the file the content of the current
        document as a string.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the native file.
        :param str content: (optional)
            Content of the file.
        :param dict values: (optional)
            Form values or request POST parameters.
        :rtype: tuple
        :return:
            A tuple such as ``(content, trust)`` where ``trust`` means:
            ``True`` valid, ``False`` invalid and ``None`` unchecked.
        """
        # From writing
        if values is not None and 'code' in values:
            return values['code'].replace('\r\n', '\n').encode('utf8'), None

        # From editing
        if values:
            native, trust = self._values2native(
                request, storage, path, content, values)
            return self._native2content(request, native), trust

        # From file
        return self._load_content(request, storage, path, content), None

    # -------------------------------------------------------------------------
    def _get_native(self, request, storage, path, content=None, values=None):
        """Get from file or from request an object depending on the native
        content of the file.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param storage: (dictionary)
            Storage dictionary.
        :param path: (string)
            Relative path to the native file.
        :param content: (string, optional)
            Content of the file to edit.
        :param values: (dictionary)
            Form values or request POST parameters.
        :return: (native object or ``None``)
        """
        # From writing
        if values is not None and 'code' in values:
            return self._content2native(request, values['code'].encode('utf8'))

        # From editing
        if values:
            return self._values2native(
                request, storage, path, content, values)[0]

        # From file
        return self._load_native(request, storage, path, content)

    # -------------------------------------------------------------------------
    @classmethod
    def _load_content(cls, request, storage, path, content=None):
        """Load the content of the file as a string.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param storage: (dictionary)
            Storage dictionary.
        :param path: (string)
            Relative path to the native file.
        :param content: (string, optional)
            Content of the file to edit.
        :return: (string or ``None``)
        """
        if content is None:
            fullname = join(
                request.registry.settings['storage.root'],
                storage['storage_id'], path)
            try:
                with open(fullname, 'rb') as hdl:
                    content = hdl.read()
            except IOError:
                return ''
        try:
            content = content.decode('utf8')
        except UnicodeDecodeError:
            pass
        return content

    # -------------------------------------------------------------------------
    def _load_native(self, request, storage, path, content=None):
        """Load an object depending on the native content of the file.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param storage: (dictionary)
            Storage dictionary.
        :param path: (string)
            Relative path to the native file.
        :param content: (string, optional)
            Initial content of the file to edit.
        :return: (native object or ``None``)
        """
        return self._load_content(request, storage, path, content)

    # -------------------------------------------------------------------------
    @classmethod
    def _content2native(cls, request, content):
        """Transform a string into a native object and validate it.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param str content:
            String to convert.
        :rtype: native object or ``None``
        """
        # pylint: disable = unused-argument
        return content

    # -------------------------------------------------------------------------
    @classmethod
    def _native2content(cls, request, native):
        """Transform a native object into a string.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :type  native: native object
        :param native:
            Object to convert.
        :rtype: :class:`str` or ``None``
        """
        # pylint: disable = unused-argument
        return native or ''

    # -------------------------------------------------------------------------
    @classmethod
    def _values2native(cls, request, storage, path, content, values):
        """Transform a dictionary of form values into a native object and
        validate it.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :param str path:
            Relative path to the native file.
        :param str content:
            Initial content.
        :param dict values:
            Values to use.
        :rtype: tuple
        :return:
            A tuple such as ``(native, is_valid)``
        """
        # pylint: disable = unused-argument
        return values.get('code', '').replace('\r\n', '\n').encode('utf8'), \
            'code' in values

    # -------------------------------------------------------------------------
    def _config_get(self, section, option, default=None):
        """Retrieve a value from a configuration object.

        :param str section:
            Section name.
        :param str option:
            Option name.
        :param str default: (optional)
            Default value
        :rtype: str
        :return:
            Read value or default value.
        """
        # Read configuration file
        if self._config_file is None:
            return default
        if self._config is None:
            config_file = join(self._path, self._config_file)
            if not exists(config_file):
                return default
            params = {
                'here': self._path,
                'main_route': MAIN_ROUTE,
                'route':  '/' + OPENER_ROUTE % self.opener_id,
                'stgpath': self._manager.settings['storage.root'],
                'lang': '{lang}', 'id': '{id}', 'ext': '{ext}', 'xml': '{xml}'}
            self._config = ConfigParser(params)
            self._config.optionxform = str
            self._config.read(config_file)

        # Read value
        if not self._config.has_option(section, option):
            return default
        value = self._config.get(section, option)
        return value.decode('utf8') if isinstance(value, str) else value

    # -------------------------------------------------------------------------
    def _load_variables_xml(self):
        """Load the variables DOM element if exists.

        :rtype: bool
        """
        if self._variables_xml is not None:
            return bool(self._variables_xml)
        self._variables_xml = self._opener_xml.findtext(
            'opener/variables/group-file')
        if self._variables_xml is None:
            self._variables_xml = ''
            return False
        self._variables_xml = load_xml(
            join(self._path, self._variables_xml),
            {'publiforge':
             join(dirname(__file__), '..', '..', 'RelaxNG', 'publiforge.rng')})
        if isinstance(self._variables_xml, basestring):
            self._variables_xml = ''
            return False
        return True

    # -------------------------------------------------------------------------
    def _edit_form(self, request, storage, variables, decode_entities=False):
        """Create the form object to edit the current file.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :type  variables: :class:`lxml.etree.ElementTree`
        :param variables:
            XML structure of variables with default values.
        :param bool decode_entities: (default=False)
            If ``True`` convert entities like &lt; into <.
        :rtype: :class:`~.lib.form.Form`
        """
        defaults = {}
        schema = self._vcs_schema(storage)
        for var in variables.findall('variables/group/var'):
            name = var.get('name')
            schema.add(variable_schema_node(name, var.get('type'), var))
            if var.find('default') is not None:
                defaults[name] = etree.tostring(
                    var.find('default'), pretty_print=True,
                    encoding='utf-8').strip()[9:-10]
                defaults[name] = defaults[name].strip().decode('utf8')
                if decode_entities:
                    defaults[name] = defaults[name].replace('&lt;', '<')\
                        .replace('&gt;', '>').replace('&amp;', '&')
                if var.get('type') == 'boolean':
                    defaults[name] = (defaults[name] == 'true')
                elif var.get('type') == 'string':
                    defaults[name] = normalize_spaces(defaults[name])

        return Form(
            request, schema=schema, defaults=defaults, force_defaults=True)

    # -------------------------------------------------------------------------
    @classmethod
    def _vcs_schema(cls, storage):
        """Base editing schema with only VCS fields.

        :param dict storage:
            Storage dictionary.
        :rtype: class:`colander.SchemaNode`
        """
        schema = SchemaNode(Mapping())
        if 'none' not in storage['vcs_engine']:
            schema.add(SchemaNode(String(), name='message', missing=None))
            schema.add(SchemaNode(
                String(), name='vcs_user',
                validator=Length(max=ID_LEN), missing=None))
            schema.add(SchemaNode(String(), name='vcs_password', missing=None))
        return schema

    # -------------------------------------------------------------------------
    @classmethod
    def _storage_handler(cls, request, storage):
        """Retrieve storage handler and user handler.

        :type  request: :class:`pyramid.request.Request`
        :param request:
            Current request.
        :param dict storage:
            Storage dictionary.
        :rtype: tuple
        :return:
            A tuple such as ``(handler, user)``
        """
        storage = current_storage(request, storage['storage_id'], False)[0]
        user = DBSession.query(StorageUser).filter_by(
            storage_id=storage.storage_id,
            user_id=request.session['user_id']).first()
        if storage.vcs_engine not in ('none', 'local') \
                and not (user and user.vcs_user):
            request.session.flash(
                _('ID and password for storage are missing.'), 'alert')
            return None, None
        user = (
            user.vcs_user, decrypt(
                user.vcs_password,
                request.registry.settings.get('encryption', '-')),
            request.session['name']) if user \
            else (None, None, request.session['name'])

        return request.registry['handler'].get_handler(
            storage.storage_id, storage), user
