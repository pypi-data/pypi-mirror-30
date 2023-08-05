# -*- coding: utf-8 -*-
"""Some various utilities."""

import re
import zipfile
import mimetypes
from sys import version_info
from os import sep, listdir, makedirs
from os.path import exists, join, isdir, dirname, basename, getmtime
from os.path import splitext
from shutil import copy2
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from unicodedata import normalize, combining
from textwrap import fill
from base64 import b64encode, b64decode
from hashlib import sha1
from random import SystemRandom, randrange
from struct import error as struct_error

from string import ascii_uppercase, digits
from Crypto.Cipher import AES
from lxml import etree
from docutils.core import publish_parts
from webhelpers2.html import literal
from PIL import Image
from PIL.ExifTags import TAGS
from piexif import load as exif_load

from pyramid.request import Request

from .i18n import _


EXCLUDED_FILES = ('.hg', '.svn', '.git', 'Thumbs.db', '.DS_Store', '_MACOSX')
MIME_TYPES = (
    'css', 'csv', 'epub+zip', 'folder', 'font-woff', 'gif', 'html',
    'indesign-iddd', 'indesign-idml', 'javascript', 'jpeg', 'mp4', 'mpeg',
    'msword', 'ogg', 'pdf', 'plain', 'png', 'postscript', 'relaxng', 'svg+xml',
    'tiff', 'vnd.ms-excel', 'vnd.ms-opentype',
    'vnd.oasis.opendocument.spreadsheet', 'vnd.oasis.opendocument.text',
    'x-msdos-program', 'x-msvideo', 'x-python', 'x-shockwave-flash', 'x-tar',
    'x-wav', 'xml', 'xml-dtd', 'zip')
NORMALIZE_FILE_MODE = {'simple': _('Simple'), 'strict': _('strict')}
EXIF_TAGS = {
    'DocumentName': 269, 'ImageDescription': 270, 'Copyright': 33432,
    'UserComment': 37510, 'ProcessingSoftware': 11, 'Software': 305}


# =============================================================================
def has_permission(request, *perms):
    """Check if the user has at least one of the specified permissions.

    :type  request: (class:`pyramid.request.Request`
    :param request:
        Current request.
    :param list perms:
        List of permission groups.
    :rtype: bool

    See :ref:`frontreference_permissions`.
    """
    if 'perms' not in request.session:
        return False
    if 'admin' in request.session['perms']:
        return True
    for perm in perms:
        if perm in request.session['perms'] or \
                '%s_manager' % perm[0:3] in request.session['perms'] or \
                ('%s_editor' % perm[0:3] in request.session['perms'] and
                 perm[4:] == 'user'):
            return True
    return False


# =============================================================================
def copy_content(src_dir, dst_dir, exclude=(), force=False):
    """Copy the content of a ``src_dir`` directory into a ``dst_dir``
    directory.

    :param src_dir: (string)
        Source directory path.
    :param dst_dir: (string)
        Destination directory path.
    :param exclude: (list, optional)
        List of files to exclude.
    :param force: (booelan, optional)
        Force copy even if the target file has the same date.
    """
    if not exists(dst_dir):
        makedirs(dst_dir)
    for name in listdir(src_dir):
        if name in exclude or name in EXCLUDED_FILES:
            continue
        source = join(src_dir, name)
        if not isinstance(source, unicode):
            source = source.decode('utf8')
            name = name.decode('utf8')
        target = join(dst_dir, name)
        if isdir(source):
            if listdir(source):
                copy_content(source, target, exclude, force)
        elif force or not exists(target) \
                or getmtime(target) != getmtime(source):
            copy2(source, target)


# =============================================================================
def camel_case(text):
    """Convert ``text`` in Camel Case."""
    if version_info[:3] >= (2, 7, 0):
        # pylint: disable = E1123
        return re.sub(
            r'(^\w|[-_ 0-9]+\w)',
            lambda m: m.group(0).replace('_', '').replace(' ', '').upper(),
            text, flags=re.UNICODE)
    return re.sub(
        r'(^\w|[-_ 0-9]+\w)',
        lambda m: m.group(0).replace('_', '').replace(' ', '').upper(), text)


# =============================================================================
def normalize_name(name):
    """Normalize name."""
    return re.sub('_+', '_', re.sub(r'[  *?!,;:"\'/]', '_', name))\
        .lower().encode('utf8')


# =============================================================================
def normalize_filename(filename, mode='simple', is_dir=False):
    """Normalize file name.

    :param filename: (string)
        File name to normalize.
    :param mode: (NORMALIZE_FILE_MODE, default='simple')
        Strategy to normalize file name.
    :param is_dir: (boolean, default=False)
        The .
    """
    result = re.sub('\\.+', '.', re.sub('[*?:]', '_', filename))
    if not is_dir:
        result = '%s%s' % (splitext(result)[0], splitext(result)[1].lower())
    if mode == 'simple':
        return result
    result = result.split(sep)
    for i, chunk in enumerate(result):
        chunk = re.sub(
            '_+', '_', re.sub(u'[  !;:,"\'/«»()\\[\\]–&]', '_', chunk))
        chunk = normalize('NFKD', chunk.encode('utf8').decode('utf8'))
        result[i] = u''.join([k for k in chunk if not combining(k)])
    if not is_dir:
        result[-1] = result[-1].lower()
    return sep.join(result)


# =============================================================================
def normalize_spaces(text, truncate=None):
    """Normalize spaces and, possibly, truncate result.

    :param str text:
        Text to normalize.
    :param int truncate: (optional)
        If not ``None``, maximum lenght of the returned string.
    :rtype: :class:`str` or ``None``
    """
    if text is None:
        return None
    text = u' '.join(text.replace(u' ', u':~:').strip().split())\
           .replace(u':~:', u' ')
    return text[0:truncate] if truncate else text


# =============================================================================
def make_id(name, mode=None, truncate=None):
    """Make an ID with name.

    :param str name:
        Name to use.
    :param int truncate: (optional)
        If not ``None``, maximum length of the returned string.
    :param str mode: ('standard', 'token', 'xmlid' or 'class', optional)
        Strategy to make ID.
    :rtype: str

    Examples of transformation of `12Test___Té*t;?!`:

    * mode = ``None``: `12test___té*t;?!`
    * mode = 'standard': `12Test_Té_t_`
    * mode = 'token': `12test_te_t_`
    * mode = 'xmlid': `_12test_te_t_`
    * mode = 'class': `12Test_Te_t_`
    """
    result = name.strip()
    if mode not in ('standard', 'class'):
        result = result.lower()
    if mode in ('standard', 'token', 'xmlid', 'class'):
        result = re.sub(
            '_+', '_', re.sub(u'[  *?!;:.,"\'/«»()\\[\\]–&]', '_', result))
    if mode in ('token', 'xmlid', 'class'):
        result = normalize('NFKD', result.encode('utf8').decode('utf8'))
        result = u''.join([k for k in result if not combining(k)])
    if mode == 'xmlid' and result and result[0].isdigit():
        result = '_%s' % result
    return result[0:truncate] if truncate else result


# =============================================================================
def wrap(text, width=70, indent=0):
    """Transform a reStructuredText into XHTML.

    :param text: (string)
        Text to wrap.
    :param width: (integer, default 70)
        The maximum length of wrapped lines.
    :param indent: (integer, default 0)
        Initial and subsequent indentation.
    :return: (string)
        Wrapped text.
    """
    text = text.strip().replace(u' ', ':~:')
    if indent:
        text = fill(
            text, initial_indent='\n' + ' ' * indent,
            subsequent_indent=' ' * indent) + '\n' + ' ' * (indent - 2)
    else:
        text = fill(text, width=width)
    return text.replace(':~:', u' ')


# =============================================================================
def hash_sha(value, key=''):
    """Cryptographic hash function with SHA1 algorithm.

    :param value: (string)
        String to hash.
    :param key: (string, optional)
        Encryption key.
    """
    return sha1(value.encode('utf8') + key.encode('utf8')).hexdigest()


# =============================================================================
def encrypt(value, key):
    """Encryption function.

    :param str value:
        String to encrypt.
    :param str key:
        Encryption key.
    :rtype: str
    :return:
        Encrypted value or ``None``.
    """
    if value:
        cipher = AES.new((str(key) * 16)[:32])
        value = value.encode('utf8')
        return b64encode(cipher.encrypt(value + b' ' * (16 - len(value) % 16)))
    return None


# =============================================================================
def decrypt(value, key):
    """Decryption function.

    :param str value:
        String to decrypt.
    :param str key:
        Encryption key.
    :rtype: str
    :return:
        Clear value or ``None``.
    """
    if value:
        cipher = AES.new((str(key) * 16)[:32])
        return cipher.decrypt(b64decode(str(value))).strip().decode('utf8')
    return None


# =============================================================================
def token(length=None):
    """Generate a token of length ``length`` or with a length between 8 an 16
    characters.

    :param int length: (optional)
        Length of the token.
    :rtype: str
    :return:
        Token.
    """
    if length is None:
        length = randrange(8, 16)
    return ''.join(
        SystemRandom().choice(ascii_uppercase + digits) for _ in range(length))


# =============================================================================
def email_is_valid(email):
    """Check the validity of an email address.

    :param str email:
        Address to check.
    :rtype: bool
    """
    return re.match(
        r'^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,6}$', email)


# =============================================================================
def unzip(archive, outpath, normalize_mode=None):
    """Extract an archive ignoring forbidden files.

    :param archive: (string or file)
        Name of the ZIP file.
    :param outpath: (string)
        Full path where extract the archive.
    :param outpath: (NORMALIZE_MODE, optional)
        Full path where extract the archive.
    """
    try:
        zip_file = zipfile.ZipFile(archive, 'r')
    except zipfile.BadZipfile:
        return
    outpath = outpath.encode('utf8')
    for zipinfo in zip_file.infolist():
        if not [k for k in EXCLUDED_FILES
                if '%s%s' % (sep, k) in zipinfo.filename]:
            if normalize_mode is not None:
                zipinfo.filename = '%s%s%s' % (
                    normalize_filename(
                        dirname(zipinfo.filename.decode('utf8')),
                        normalize_mode, True),
                    sep,
                    normalize_filename(
                        basename(zipinfo.filename.decode('utf8')),
                        normalize_mode))
            zip_file.extract(zipinfo, outpath)
    zip_file.close()


# =============================================================================
def get_mime_type(filename):
    """Return the mime type of ``filename``.

    :param filename: (string)
        File name.
    :return: (tuple)
        A tuple such as ``(mime_type, subtype)``. For instance:
        ``('text/plain', 'plain')``.
    """
    if isdir(filename):
        return 'folder', 'folder'
    mimetype = mimetypes.guess_type(filename, False)[0]
    if mimetype is None:
        return 'unknown', 'unknown'
    subtype = mimetype.partition('/')[2]
    return mimetype, subtype or mimetype


# =============================================================================
def size_label(size, is_dir):
    """Return a size in o, Kio, Mio or Gio.

    :param size: (integer)
        Size in figures.
    :param is_dir: (boolean)
        ``True`` if it is about a directory.
    :return: (string or :class:`pyramid.i18n.TranslationString`)
    """
    # For a directory
    if is_dir:
        return _('${n} items', {'n': size}) if size > 1 else \
            _('${n} item', {'n': size})

    # For a file
    if size >= 1073741824:
        return '%.1f Gio' % round(size / 1073741824.0, 1)
    elif size >= 1048576:
        return '%.1f Mio' % round(size / 1048576.0, 1)
    elif size >= 1024:
        return '%.1f Kio' % round(size / 1024.0, 1)
    return '%d o' % size


# =============================================================================
def age(mtime):
    """Return an age in minutes, hours, days or date.

    :param mtime: (datetime)
        Modification time.
    :return: (:class:`pyramid.i18n.TranslationString` or string)
        Return an age or a date if ``mtime`` is older than a year.
    """
    # pylint: disable = R0911
    if not mtime:
        return ''
    delta = datetime.now() - mtime
    if delta.days == 0 and delta.seconds < 60:
        return _('1 second') if delta.seconds <= 1 \
            else _('${s} seconds', {'s': delta.seconds})
    elif delta.days == 0 and delta.seconds < 3600:
        minutes = int(round(delta.seconds / 60))
        return _('1 minute') if minutes == 1 \
            else _('${m} minutes', {'m': minutes})
    elif delta.days == 0:
        hours = int(round(delta.seconds / 3600))
        return _('1 hour') if hours == 1 \
            else _('${h} hours', {'h': hours})
    elif delta.days < 7:
        return _('1 day') if delta.days == 1 \
            else _('${d} days', {'d': delta.days})
    elif delta.days < 30:
        weeks = int(round(delta.days / 7))
        return _('1 week') if weeks == 1 \
            else _('${w} weeks', {'w': weeks})
    elif delta.days < 365:
        months = int(round(delta.days / 30))
        return _('1 month') if months == 1 else \
            _('${m} months', {'m': months})
    return str(mtime.replace(microsecond=0))[0:-9]


# =============================================================================
def duration(request, seconds):
    """Return a duration in seconds, minutes, hours and days.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param seconds: (integer)
        Number of seconds to convert.
    :return: (string)
    """
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    translate = request.localizer.translate
    text = ''
    if days:
        text += days > 1 and \
            translate(_('${d} days ', {'d': days})) or \
            translate(_('${d} day ', {'d': days}))
    if hours:
        text += hours > 1 and \
            translate(_('${h} hours ', {'h': hours})) or \
            translate(_('${h} hour ', {'h': hours}))
    if minutes:
        text += minutes > 1 and \
            translate(_('${m} minutes ', {'m': minutes})) or \
            translate(_('${m} minute ', {'m': minutes}))
    if seconds:
        text += seconds > 1 and \
            translate(_('${s} seconds', {'s': seconds})) or \
            translate(_('${s} second', {'s': seconds}))

    return text


# =============================================================================
def cache_key(cache, method_name, *args):
    """Compute a cache key.

    :param cache: (:class:`beaker.cache.Cache` instance)
    :param method_name: (string)
    :param args: (positional arguments)
    :return: (string)
    """
    if args and isinstance(args[0], Request):
        args = args[1:]
    try:
        key = ','.join([str(k) for k in args])
    except UnicodeEncodeError:
        key = ','.join([unicode(k) for k in args])
    key = '%s(%s)' % (method_name, key)
    if len(key) + len(cache.namespace_name) > 250:
        key = sha1(key.encode('utf8')).hexdigest()
    return key


# =============================================================================
def cache_decorator():
    """Decorator to cache a method of a class with ``self.cache`` attribute.

    ``self.cache`` is a :class:`beaker.cache.Cache` instance.

    The method being decorated must only be called with positional arguments,
    and the arguments must support being stringified with ``str()``.
    """
    def _wrapper(create_method):
        """Wrapper function."""

        def _cached(self, *args):
            """Cache function."""
            if not hasattr(self, 'cache'):
                raise Exception('Class must have a "cache" attribute!')
            key = cache_key(self.cache, create_method.__name__, *args)

            def _createfunc():
                """Creation function."""
                return create_method(self, *args)

            return self.cache.get_value(key, createfunc=_createfunc)

        return _cached

    return _wrapper


# =============================================================================
def export_file_set(root_elt, record, file_type):
    """Save set of files in a XML object.

    :param root_elt: (:class:`lxml.etree.Element` instance)
        Element that linked the result.
    :param record: (:class:`~.models.processings.Processing`
        or :class:`~.models.packs.Pack` instance).
    :param file_type: ('file', 'resource' or 'template')
        File type.
     """
    items = [k for k in record.files if k.file_type == file_type]
    if not items:
        return
    group_elt = etree.SubElement(root_elt, '%ss' % file_type)
    for item in sorted(items, key=lambda k: k.sort):
        elt = etree.SubElement(group_elt, file_type)
        if hasattr(item, 'target') and item.target:
            elt.set('to', item.target)
        if hasattr(item, 'visible') \
                and not (file_type == 'file' and item.visible) \
                and not (file_type != 'file' and not item.visible):
            elt.set('visible', item.visible and 'true' or 'false')
        elt.text = item.path


# =============================================================================
def shift_files(direction, index, record, files, form):
    """Shift a file in the list of files of a record (pack or processing).

    :param direction: ('mup' or 'dwn')
        Direction of the move.
    :param index: (string)
        Item to move in ``files``.
    :param record: (:class:`~.models.processings.Processing` or
        :class:`~.models.packs.Pack` instance)
        Current pack object.
    :param files: (dictionary)
        See :func:`~.lib.viewutils.file_details` function.
    :param form: (:class:`~.lib.form.Form` instance)
        Current form
    """
    file_type, index = index.partition('_')[0::2]
    index = int(index)

    # Something to do?
    direction = 1 if direction == 'dwn' else -1
    if (direction == -1 and index == 0) \
       or (direction == 1 and index + 1 == len(files[file_type])):
        return

    # Swap in database
    item1 = '%s/%s' % files[file_type][index][1:3]
    item1 = [k for k in record.files
             if k.file_type == file_type and k.path == item1][0]
    item2 = '%s/%s' % files[file_type][index + direction][1:3]
    item2 = [k for k in record.files
             if k.file_type == file_type and k.path == item2][0]
    item1.sort, item2.sort = item2.sort, item1.sort

    # Swap in dictionary
    files[file_type][index], files[file_type][index + direction] = \
        files[file_type][index + direction], files[file_type][index]

    # Modify form
    if form is not None and hasattr(item1, 'visible'):
        form.values['%s_%d_see' % (file_type, index)] = item2.visible
        form.values['%s_%d_see' % (file_type, index + direction)] = \
            item1.visible
        form.static('%s_%d_see' % (file_type, index))
        form.static('%s_%d_see' % (file_type, index + direction))


# =============================================================================
def execute(command, cwd=None, no_exit_code=False):
    """Run the command described by command. Wait for command to complete.
    If the return code is not zero, return output and an error message.

    :param command: (list)
        Splitted command to execute.
    :param cwd: (string, optional)
        If it is not ``None``, the current directory will be changed to ``cwd``
        before it is executed.
    :param no_exit_code: (boolean, default=False)
        If the command is known to exit with code 0 even if there is an error,
        assign this argument to ``True``.
    :return: (tuple)
        An error message such as ``(output, error)`` where ``output`` is a
        string and ``error`` a :class:`pyramid.i18n.TranslationString`.
    """
    try:
        process = Popen(command, cwd=cwd, stderr=STDOUT, stdout=PIPE)
    except OSError as error:
        return '', _('"${c}" failed: ${e}', {'c': command, 'e': error})
    if command[0] == 'nice':
        command = command[1:]
    command = basename(command[0])
    try:
        output = process.communicate()[0]
        if process.poll() or (no_exit_code and output):
            try:
                return output[0:102400].decode('utf8').strip(), \
                    _('"${c}" failed', {'c': command})
            except UnicodeDecodeError:
                return output[0:102400].decode('latin1').strip(), \
                    _('"${c}" failed', {'c': command})
    except OSError as error:
        return '', _('"${c}" failed: ${e}', {'c': command, 'e': error})
    output = output[0:102400]
    try:
        output = output.decode('utf8')
    except UnicodeDecodeError:
        pass
    return output.strip(), ''


# =============================================================================
def rst2xhtml(rst):
    """Transform a reStructuredText into XHTML.

    :param str rst:
        reStructuredText.
    :rtype: str
    :return:
        XHTML.
    """
    return literal(publish_parts(rst, writer_name='html')['body'].replace(
        'blockquote', 'div')) if rst else None


# =============================================================================
def load_regex(filename):
    """Load a list of regular expressions.

    :param filename: (string)
        Name of file to load.
    :return: (list)
        A list of :class:`re.pattern` objects.
    """
    regex = []
    for line in open(filename, 'r'):
        if line and line[0] != '#' and line[0:7] != '[Regex]':
            pattern, replace = line.partition(' =')[::2]
            pattern = pattern.strip().decode('utf8')
            if not pattern:
                continue
            if pattern[0] in '\'"' and pattern[-1] in '\'"':
                pattern = pattern[1:-1]
            replace = replace.strip().decode('utf8')
            if replace and replace[0] in '\'"' and replace[-1] in '\'"':
                replace = replace[1:-1]
            # pylint: disable = eval-used
            if replace.startswith('lambda'):
                replace = eval(replace)
            regex.append((re.compile(
                pattern, re.MULTILINE | re.UNICODE), replace))

    return regex


# =============================================================================
def image_metadata(img_file):
    """Retrieve metadata (exif or XMP) of the image.

    :param str img_file:
        Absolute path to the image file.
    :rtype: tuple
    :return:
        A tuple such as ``(title, description, size)``.
    """
    metadata = {}
    try:
        image = Image.open(img_file)
    except (IOError, ValueError, ZeroDivisionError):
        return {}
    metadata = {'size': image.size}

    # JPEG
    if image.format == 'JPEG' and 'exif' in image.info:
        try:
            exif = exif_load(image.info['exif'])
        except (struct_error, ValueError):
            image.close()
            return metadata
        if exif:
            for tag in exif['0th']:
                if tag in TAGS and TAGS[tag] in EXIF_TAGS:
                    metadata[TAGS[tag]] = exif['0th'][tag].decode(
                        'utf8', 'replace')
        image.close()
        return metadata

    # PNG
    elif image.format == 'PNG' and 'XML:com.adobe.xmp' in image.info:
        tree = etree.XML(image.info['XML:com.adobe.xmp'])
        metadata['DocumentName'] = tree.findtext(
            './/{http://purl.org/dc/elements/1.1/}title/'
            '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Alt/'
            '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li')
        metadata['ImageDescription'] = tree.findtext(
            './/{http://purl.org/dc/elements/1.1/}description/'
            '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Alt/'
            '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li')
        image.close()
        return metadata

    image.close()
    return metadata
