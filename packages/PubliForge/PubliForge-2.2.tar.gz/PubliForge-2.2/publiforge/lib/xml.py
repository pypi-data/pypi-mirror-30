"""XML manipulation."""

from os.path import join, dirname, basename, relpath
from io import BytesIO
from textwrap import wrap
from warnings import warn

from lxml import etree

from pyramid.httpexceptions import HTTPForbidden
from pyramid.response import Response

from .i18n import _
from .utils import has_permission, normalize_name, normalize_spaces
from .utils import camel_case, make_id
from ..models.users import User
from ..models.groups import Group
from ..models.storages import Storage
from ..models.indexers import Indexer
from ..models.projects import Project


XML_NS = '{http://www.w3.org/XML/1998/namespace}'
PUBLIFORGE_RNG_VERSION = '1.0'
PF_NAMESPACE = 'http://publiforge.org/functions'
EXTENSIONS = {
    'user': 'pfusr', 'group': 'pfgrp', 'indexer': 'pfidx', 'storage': 'pfstg',
    'project': 'pfprj', 'processing': 'pfprc', 'pack': 'pfpck'}


# =============================================================================
def load_xml(filename, relaxngs=None, data=None, noline=False, parser=None):
    """Load an XML document and validate it against a Relax NG file.

    :param str filename:
        Path to XML file.
    :param dict relaxngs: (optional)
        Relax NG dictionary such as ``{<pattern>: <relax_ng_file>,...}``. If it
        is ``None``, no validation is performed.
    :type data: str, bytes or :class:`lxml.etree.ElementTree`
    :param data: (optional)
        Content of the XML document. If it is not ``None``, it is used in place
        of the content of the file ``filename``.
    :param bool noline: (default=False)
        If ``True``, the error message does not contain line numbers.
    :type parser: class:`etree.XMLParser`
    :param parser: (optional)
        Specific parser for ``etree.parse`` function.
    :rtype: str, :class:`TranslationString` or :class:`ElementTree`
    :return:
        An error message or an instance of :class:`lxml.etree.ElementTree`
        class.
    """
    # Read file
    # pylint: disable = protected-access
    if data is None or not isinstance(data, etree._ElementTree):
        if data is not None and not isinstance(data, bytes):
            data = bytes(data.encode())
        try:
            tree = etree.parse(
                filename if data is None else BytesIO(data), parser=parser)
        except IOError:
            return _('Unknown file "${n}"', {'n': basename(filename)})
        except etree.XMLSyntaxError as error:
            return str(error)
    else:
        tree = data
    # pylint: enable = protected-access

    # Validate
    if relaxngs is None:
        return tree
    error = validate_xml(tree, relaxngs, noline)
    if error is not None:
        return error

    return tree


# =============================================================================
def load(filename, relaxngs=None, data=None, noline=False, parser=None):
    """Legacy function."""
    warn('Deprecated: use publiforge.lib.xml.load_xml()', DeprecationWarning)
    return load_xml(filename, relaxngs, data, noline, parser)


# =============================================================================
def validate_xml(tree, relaxngs, noline=False):
    """Load an XML document and validate it against a Relax NG file.

    :type  tree: :class:`lxml.etree.ElementTree`
    :param tree:
        XML document.
    :param dict relaxngs:
        Relax NG dictionary such as ``{<pattern>: <relax_ng_file>,...}``.
    :param bool noline: (default=False)
        If ``True``, the error message does not contain line numbers.
    :rtype: str, :class:`TranslationString` or ``None``
    :return:
        An error message or ``None``.
    """
    # Find the right RelaxNG
    relaxng = None
    root = tree.getroot()
    for name in relaxngs:
        chunks = name.split(',')
        chunk = chunks[0].strip()
        if root.tag != chunk:
            continue
        for chunk in chunks[1:]:
            chunk = chunk.split()
            if root.get(chunk[0]) != chunk[1]:
                chunk = None
                break
        if chunk is not None:
            relaxng = relaxngs[name]
            break
    if relaxng is None:
        return _('${tag}: Relax NG not found', {'tag': tree.getroot().tag})

    # Load Relax NG
    if isinstance(relaxng, str):
        try:
            relaxng = etree.RelaxNG(etree.parse(relaxng))
        except IOError as error:
            return str(error)
        except (etree.XMLSyntaxError, etree.RelaxNGParseError) as error:
            return '"{0}": {1}'.format(relaxng, error)

    # Validate
    if not relaxng.validate(tree):
        error = relaxng.error_log.last_error
        return error.message if noline else \
            _('Line ${l}: ${m}', {'l': error.line, 'm': error.message})
    return None


# =============================================================================
def local_text(root_elt, xpath, request=None, lang=None, default=''):
    """Return the text in local language of the ``root_elt`` element child
    selected by ``xpath``.

    :param root_elt: (:class:`lxml.etree.Element` instance)
        Root element.
    :param xpath: (string)
        XPath expression.
    :param request: (:class:`pyramid.request.Request` instance, optional)
        Current request.
    :param lang: (string, optional)
        Preferred language.
    :param default: (string, optional)
        Default label.
    :return: (string)

    If label does not exist in the asked language, this method returns the
    label in default language or in english or the first label or ''.
    """
    if lang is None and request is None:
        return default

    lang = lang or request.session['lang']
    lang_xpath = xpath + '[@xml:lang="%s"]'
    text = root_elt.xpath(lang_xpath % lang) \
        or root_elt.xpath(lang_xpath % lang.split('_')[0])
    if not text and request is not None:
        lang = request.registry.settings.get(
            'pyramid.default_locale_name', 'en')
        text = root_elt.xpath(lang_xpath % lang) \
            or root_elt.xpath(lang_xpath % lang.split('_')[0])
    if not text:
        text = root_elt.xpath(lang_xpath % 'en')

    text = (len(text) == 1 and text[0].text) \
        or (root_elt.find(xpath) is not None and root_elt.find(xpath).text) \
        or default

    return normalize_spaces(text)


# =============================================================================
def upload_configuration(request, perm, only=None):
    """Upload a XML configuration file.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param perm: (string)
        Level of permission needed.
    :param only: (string, optional)
        ``user``, ``group``, ``storage`` or ``project``.
    """
    if not has_permission(request, perm):
        raise HTTPForbidden()

    xml_file = request.params.get('xml_file')
    if isinstance(xml_file, basestring):
        return

    errors = import_configuration(
        request.registry.settings, xml_file.filename, only=only,
        xml=xml_file.file.read(), request=request)
    for error in errors:
        request.session.flash(error, 'alert')


# =============================================================================
def import_configuration(settings, filename, only=None, error_if_exists=True,
                         xml=None, request=None):
    """Import a XML configuration file.

    :param settings: (dictionary)
        Application settings
    :param filename: (string)
        Full path to file to import.
    :param only: (string, optional)
        ``user``, ``group``, ``storage``, ``indexer`` or ``project``.
    :param error_if_exists: (boolean, default=True)
        It returns an error if an item already exists.
    :param xml: (string, optional)
        Content of the XML document.
    :param request: (:class:`pyramid.request.Request` instance, optional)
        Current request.
    :return: (list)
        A list of error messages.
    """
    # pylint: disable = R0912
    # Load XML
    tree = load_xml(
        filename,
        {'publiforge':
         join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')}, xml)
    if isinstance(tree, basestring):
        return (tree,)

    # Load users
    # pylint: disable = E1103
    errors = []
    if only is None or only == 'user':
        for elt in tree.xpath('user|users/user'):
            errors.append(User.load(settings, elt, error_if_exists))

    # Load groups
    if only is None or only == 'group':
        for elt in tree.xpath('group|groups/group'):
            errors.append(Group.load(elt, error_if_exists))

    # Load storages
    if only is None or only == 'storage':
        for elt in tree.xpath('storage|storages/storage'):
            storage = Storage.load(settings, elt, error_if_exists)
            if isinstance(storage, basestring):
                errors.append(storage)
            elif storage is not None and request is not None:
                handler = request.registry['handler']\
                    .get_handler(storage.storage_id, storage)
                handler.clone(request)

    # Load indexers
    if only is None or only == 'indexer':
        for elt in tree.xpath('indexer|indexers/indexer'):
            errors.append(Indexer.load(elt, error_if_exists))

    # Load projects
    if only is None or only == 'project':
        for elt in tree.xpath('project|projects/project'):
            errors.append(Project.load(elt, error_if_exists))

    return [k for k in errors if k is not None]


# =============================================================================
def export_configuration(elements, filename=None, command=False):
    """Export an XML configuration and return it as a
    :class:`pyramid.response.Response` object.

    :param elements: (list)
        List of :class:`lxml.etree.Element` objects.
    :param filename: (string, optional)
        Name of file to export. Default to ``'publiforge'``.
    :param command: (boolean, default=False)
        ``True`` if called by command line.
    :return: (:class:`pyramid.response.Response` instance)
    """
    def _label(elt):
        """Get label or name of ``elt``."""
        label = elt.get('%sid' % XML_NS) or elt.get('login') \
            or (elt.findtext('label') is not None and elt.findtext('label'))
        return normalize_spaces(label)

    # Nothing to do
    if not elements:
        raise HTTPForbidden()

    # Create XML document
    root = etree.Element('publiforge', version=PUBLIFORGE_RNG_VERSION)

    # Single export
    if len(elements) == 1:
        label = _label(elements[0])
        root.append(etree.Comment('=' * 70))
        root.append(etree.Comment(u'{0:^70}'.format(label)))
        root.append(etree.Comment('=' * 70))
        root.append(elements[0])
        filename = '%s.%s' % (label, EXTENSIONS.get(elements[0].tag, 'pf'))
    # Multiple export
    else:
        for name in ('user', 'group', 'storage', 'indexer',
                     'project', 'processing', 'pack'):
            elts = [k for k in elements if k is not None and k.tag == name]
            if not elts:
                continue
            root.append(etree.Comment('=' * 70))
            root.append(etree.Comment(u'{0:^70}'.format(
                '%ss' % name.capitalize())))
            root.append(etree.Comment('=' * 70))
            grouper = etree.SubElement(root, '%ss' % name)
            for elt in elts:
                grouper.append(etree.Comment(' ' * 68))
                grouper.append(etree.Comment(
                    u'{0:=^68}'.format(' %s ' % _label(elt))))
                grouper.append(etree.Comment(' ' * 68))
                grouper.append(elt)
        filename = filename or 'publiforge'

    # Command line
    if command:
        root = etree.ElementTree(root)
        root.write(
            filename, pretty_print=True, encoding='utf-8',
            xml_declaration=True)
        return None

    # Response
    response = Response(
        body=etree.tostring(
            root, pretty_print=True, encoding='utf-8', xml_declaration=True),
        content_type='application/xml')
    response.headerlist.append((
        'Content-Disposition',
        'attachment; filename="%s.xml"' % normalize_name(filename)))
    return response


# =============================================================================
def xml_wrap(text, depth):
    """Return a dictionary with the localized texts contained in an XML
    element.

    :param str text:
        Text to wrap and indent.
    :param int depth:
        Depth of the parent element in the entire XML structure.
    :rtype: str
    """
    indent = u' ' * 2 * (depth + 1)
    return u'\n{0}\n{1}'.format(
        u'\n'.join(
            [u'{0}{1}'.format(indent, k)
             for k in wrap(text, 79 - 2 * (depth + 1))]), u' ' * 2 * depth)


# =============================================================================
def xpath_camel_case(context, text):
    """XPath function:  camel_case()."""
    # pylint: disable = W0613
    return camel_case(text)


# =============================================================================
def xpath_make_id(context, name, mode):
    """XPath function:  make_id()."""
    # pylint: disable = W0613
    return make_id(name, mode)


# =============================================================================
def xpath_relpath(context, path, start):
    """XPath function:  relpath()."""
    # pylint: disable = W0613
    return relpath(path, start)


# =============================================================================
def xpath_wrap(context, text, depth):
    """XPath function:  xml_wrap()."""
    # pylint: disable = unused-argument
    return xml_wrap(text, int(depth))


# =============================================================================
def _relaxng(relaxngs, root):
    """Find the right Relax NG among ``relaxngs`` according to ``root``
    element.

    :param relaxngs: (dictionary)
    :param root: (:class:`lxml.etree.Element` instance)
    :return: (string or :class:`lxml.etree.RelaxNG` or ``None``)
    """
    for name in relaxngs:
        chunks = name.split(',')
        chunk = chunks[0].strip()
        if root.tag != chunk:
            continue
        for chunk in chunks[1:]:
            chunk = chunk.split()
            if root.get(chunk[0]) != chunk[1]:
                chunk = None
                break
        if chunk is not None:
            return relaxngs[name]
    return None
