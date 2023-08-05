"""LePrisme module transforms files into another files or values."""

import re
from os import walk, listdir, makedirs, remove, rmdir
from os.path import join, exists, splitext, dirname, basename, isdir, relpath
from os.path import normpath, samefile, commonprefix
from shutil import copy, rmtree
from ConfigParser import ConfigParser
from zipfile import is_zipfile
from imp import load_source
from lxml import etree

from ...i18n import _
from ...config import config_get, config_get_list
from ...utils import copy_content, unzip, camel_case, make_id
from ...xml import load_xml
from .. import load_relaxngs
from .publiset import Publiset
from .transform import Transform


REMOVE_PATTERN = r'(~|\.tmp)(\.\w{1,4})?$'


# =============================================================================
class Processor(object):
    """Main class for LePrisme processor."""

    # -------------------------------------------------------------------------
    def __init__(self, build):
        """Constructor method.

        :param build: (:class:`~.lib.build.agent.AgentBuild`)
            Main Build object.
        """
        # Attributes
        self.build = build
        self.output = join(self.build.path, 'Output')
        self.percents = [1, 90]

        # Configuration
        name = join(build.path, 'Processor', 'leprisme.ini')
        if not exists(name):
            build.stopped(_('File "leprisme.ini" is missing.'))
            return
        self._config = ConfigParser({
            'here': dirname(name), 'fid': '{fid}', 'ocffile': '{ocffile}'})
        self._config.optionxform = str
        self._config.read(name)

        # Transformation steps
        steps = self._read_steps()
        if not steps:
            build.stopped(_('Transformation steps are missing.'))
            return

        # Relax NG, scripts and transformation
        self.relaxngs = load_relaxngs(self.build, self._config)
        self._scripts = self._load_scripts()
        self._transform = Transform(self, steps)

    # -------------------------------------------------------------------------
    def start(self):
        """Start the processor."""
        if self.build.stopped():
            return

        # Process each file
        files = self._file_list()
        if not files:
            self.build.stopped(_('nothing to do!'), 'a_error')
            return
        for count, name in enumerate(files):
            self._process(
                name, 90 * count / len(files), 90 * (count + 1) / len(files))
            if self.build.stopped():
                break

        # Finalization
        if not self.build.processing['variables'].get('subdir'):
            self.output = join(self.build.path, 'Output')
            self.finalize()

    # -------------------------------------------------------------------------
    def config(self, section, option, default=None):
        """Retrieve a value from a configuration object.

        :param section: (string)
            Section name.
        :param option: (string)
            Option name.
        :param default: (string, optional)
            Default value
        :return: (string)
            Read value or default value.
        """
        return config_get(self._config, section, option, default)

    # -------------------------------------------------------------------------
    def config_list(self, section, option, default=None):
        """Retrieve a list of values from a configuration object.

        :param section: (string)
            Section name.
        :param option: (string)
            Option name.
        :param default: (list, optional)
            Default values.
        :return: (list)
        """
        return config_get_list(self._config, section, option, default)

    # -------------------------------------------------------------------------
    def make_id(self, fullname):
        """Compute a file ID according to processor configuration.

        :param fullname: (string)
            Absolute path to file to process.
        """
        mode = self.config('Output', 'make_id', 'token') or 'token'
        if mode in ('standard', 'token', 'xmlid', 'class'):
            return make_id(splitext(basename(fullname))[0], mode)

        if not exists(mode):
            self.build.stopped(
                _('Unknown file "${n}".', {'n': basename(mode)}))
            return None

        module = load_source(splitext(basename(mode))[0], mode)
        return module.make_id(fullname, self.build, self._config)

    # -------------------------------------------------------------------------
    def finalize(self):
        """Finalization."""
        # Remove temporary files
        if not self.build.processing['variables'].get('keeptmp'):
            self._remove_temporary_files(self.output)

        # Run finalization script
        if 'finalization' in self._scripts:
            self._scripts['finalization'](self)

    # -------------------------------------------------------------------------
    def _read_steps(self):
        """Detect in configuration file the names of the transformation steps.

        :return: (tuple)
            A tuple of suffix for ``[Transformation]`` section.
        """
        steps = []
        for section in self._config.sections():
            if section.startswith('Transformation'):
                if self._config.has_option(section, 'inactive'):
                    inactive = self._config.get(section, 'inactive')
                    variable = self.build.processing['variables'].get(
                        inactive.replace('!', ''))
                    if (inactive[0] == '!' and not variable) \
                       or (inactive[0] != '!' and variable):
                        continue
                steps.append(section[14:])
        return tuple(steps)

    # -------------------------------------------------------------------------
    def _load_scripts(self):
        """Load initialization and finalization script files.

        :return: (dictionary)
            A dictionary of script main functions.
         """
        scripts = {}
        for section in ('Initialization', 'Finalization'):
            # Find file
            filename = self.config(section, 'script')
            if not filename:
                continue
            if not exists(filename):
                self.build.stopped(_('Unknown file "${n}".', {'n': filename}))
                continue

            # Load module
            module = load_source(splitext(basename(filename))[0], filename)
            scripts[section.lower()] = module.main

        return scripts

    # -------------------------------------------------------------------------
    def _update_output(self, filename, fid):
        """Compute output directory for file ``filename``.

        :param filename: (string)
            Relative path to the original file to transform.
        :param fid: (string)
            File ID.
        :return: (string)
            Output path.
        """
        subdir = self.build.processing['variables'].get('subdir')
        if subdir:
            prefix = commonprefix(
                tuple(self.build.pack['files']) + (filename,))
            if not isdir(prefix):
                prefix = dirname(prefix)
            path = relpath(filename, prefix)
            parent = basename(dirname(filename)) \
                if dirname(dirname(filename)) else ''
            self.output = join(
                self.build.path, 'Output',
                subdir.replace('%(fid)s', camel_case(fid))
                .replace('%(path)s', dirname(path))
                .replace('%(parent)s', parent))
        else:
            self.output = join(self.build.path, 'Output')

    # -------------------------------------------------------------------------
    def _file_list(self):
        """List files in pack according to settings.

        :return: (list)
            File list.
        """
        regex = self._config.has_option('Input', 'file_regex') \
            and re.compile(self.config('Input', 'file_regex'))
        input_is_dir = self._config.has_option('Input', 'is_dir') \
            and self.config('Input', 'is_dir') == 'true'
        files = []

        for base in self.build.pack['files']:
            fullname = normpath(join(self.build.data_path, base))
            if not exists(fullname):
                self.build.stopped(_('Unknown file "${n}".', {'n': base}))
                continue

            if (not regex or regex.search(base)) \
                    and isdir(fullname) == input_is_dir:
                files.append(base)
            if not isdir(fullname):
                if base not in files:
                    self.build.log(
                        _('"${n}" ignored', {'n': base}), step='a_build')
                continue

            if self.build.pack.get('recursive'):
                for path, dirs, filenames in walk(fullname):
                    names = dirs if input_is_dir else filenames
                    for name in names:
                        if not regex or regex.search(name):
                            name = relpath(
                                join(path, name), self.build.data_path)
                            name = unicode(name.decode('utf8')) \
                                if isinstance(name, str) else name
                            files.append(name)
            else:
                for name in listdir(fullname):
                    if isdir(join(fullname, name)) == input_is_dir \
                            and (not regex or regex.search(name)):
                        name = relpath(
                            join(fullname, name), self.build.data_path)
                        name = unicode(name.decode('utf8')) \
                            if isinstance(name, str) else name
                        files.append(name)

        return files

    # -------------------------------------------------------------------------
    def _initialize(self, fid):
        """Initialization.

        :param fid: (string)
            File ID.

        ``self.build.processing['templates']`` and
        ``self.build.pack['templates']`` are lists of tuples such as
        ``(<input_file>, <output_path>)``.
        """
        # Check
        if not self.output.startswith(self.build.path):
            self.build.stopped(_('file outside build directory'))
            return

        # Clean up
        # pylint: disable = no-member
        if not exists(self.output):
            makedirs(self.output)
        fmt = self.config('Output', 'format')
        if fmt and exists(join(self.output, fmt.format(fid=fid))) and \
           not isdir(join(self.output, fmt.format(fid=fid))):
            remove(join(self.output, fmt.format(fid=fid)))
        if not self.build.processing['variables'].get('keeptmp'):
            self._remove_temporary_files(
                self.output,
                self._config.has_option('Input', 'unzip') and '%s~' % fid)

        # Create directories
        for name in self.config_list('Initialization', 'directories'):
            name = name.format(fid=fid)
            if name and not exists(join(self.output, name)):
                makedirs(join(self.output, name))

        # Copy templates
        if not self._copy_templates(fid):
            return

        # Run initialization script
        if 'initialization' in self._scripts:
            self._scripts['initialization'](self)

    # -------------------------------------------------------------------------
    def _process(self, filename, percent_in, percent_out, file_elt=None):
        """Process one XML file.

        :param str filename:
            Relative path of the file to process.
        :param int percent_in:
            Percent of progress by entering the processing.
        :param int percent_out:
            Percent of progress by leaving the processing.
        :type  file_elt: lxml.etree.Element
        :param file_elt: (optional)
            <file> XML element for the current file.
        """
        # Load path
        fullname = normpath(join(self.build.data_path, filename))
        fid = self.make_id(fullname)
        if self.build.stopped():
            return
        self.percents = [max(percent_in, 1), percent_out]
        self.build.log(
            u'---------- %s (%s)' % (filename, fid), step='a_build',
            percent=self.percents[0])
        self._update_output(filename, fid)

        # Load folder
        if isdir(fullname) or \
                (self._config.has_option('Input', 'no_load') and
                 self.config('Input', 'no_load') == 'true'):
            self._initialize(fid)
            self._transform.start(filename, fid, filename)
            return

        # Unzip file
        if self.config('Input', 'unzip') and is_zipfile(fullname):
            self.percents[0] = min(self.percents[0] + 1, self.percents[1])
            self.build.log(
                _('${f}: uncompressing', {'f': fid}), percent=self.percents[0])
            unzip(fullname, join(self.output, '%s~' % fid))
            fullname = join(
                self.output, '%s~' % fid, self.config('Input', 'unzip'))

        # Load file content
        self.percents[0] = min(self.percents[0] + 1, self.percents[1])
        self.build.log(
            _('${f}: loading file content', {'f': fid}),
            percent=self.percents[0])
        data = self._file_content(fullname, filename)
        if data is None:
            if self._config.has_option('Input', 'unzip') \
                    and isdir(join(self.output, '%s~' % fid)):
                rmtree(join(self.output, '%s~' % fid))
            return

        # Non Publiset file
        # pylint: disable = E1103
        if isinstance(data, basestring) or data.getroot().tag != 'publiset' or\
           self.config('Input', 'no_composition') == 'true':
            self._initialize(fid)
            self._add_pi(data, file_elt)
            self._transform.start(filename, fid, data)
            return

        # Publiset selection
        publiset = Publiset(self, dirname(fullname))
        set_root = data.find('composition') \
            if self.config('Input', 'as_selection') == 'true' and \
            data.find('composition') is not None else data.find('selection')
        if set_root is not None:
            fid = set_root.get('id') or fid
            for elt in set_root.xpath('.//file'):
                name = relpath(
                    publiset.fullname(elt), self.build.data_path)
                if name != filename:
                    self._process(name, percent_in, percent_out, elt)
                if self.build.stopped():
                    return
            self.build.log(
                u'%s ............' % fid, step='a_build',
                percent=self.percents[0])
            self._update_output(filename, fid)
            self._initialize(fid)
            if data.find('composition') is not None and \
               self.config('Input', 'no_composition') != 'true':
                self._transform.start(
                    filename, fid, publiset.compose(filename, set_root))
            else:
                self._transform.start(filename, fid, publiset.create(set_root))
            return

        # Publiset composition
        set_root = data.find('composition')
        fid = set_root.get('id') or fid
        self.percents[0] = min(self.percents[0] + 1, self.percents[1])
        self.build.log(_('${f}: document composition', {'f': fid}))
        self._update_output(filename, fid)
        self._initialize(fid)
        self._transform.start(
            filename, fid, publiset.compose(filename, set_root))

    # -------------------------------------------------------------------------
    def _file_content(self, fullname, filename):
        """Load file content.

        :param fullname: (string)
            Absolute path to file to load.
        :param filename: (string)
            Relative path for messages.
        :return: (string or :class:`lxml.etree.ElementTree` instance or
            ``None``)
        """
        # Content regex
        regex = self.config('Input', 'content_regex')

        # XML file
        if splitext(fullname)[1].lower() == '.xml':
            relaxngs = self.relaxngs \
                if self.config('Input', 'validate') == 'true' else None
            data = load_xml(fullname, relaxngs)
            if not isinstance(data, basestring) and \
               (not regex or re.search(regex, etree.tostring(data))):
                return data
            if isinstance(data, basestring):
                if regex and exists(fullname):
                    with open(fullname, 'r') as hdl:
                        data = re.search(regex, hdl.read()) and data
                self.build.stopped(data, 'a_error')
            self.build.log(
                _('"${n}" ignored', {'n': filename}), step='a_build')
        # Other
        elif exists(fullname):
            with open(fullname, 'r') as hdl:
                data = hdl.read()
            if not regex or re.search(regex, data):
                return data
            self.build.log(
                _('"${n}" ignored', {'n': filename}), step='a_build')
        else:
            self.build.stopped(_('Unknown file "${n}".', {'n': filename}))
        return None

    # -------------------------------------------------------------------------
    @classmethod
    def _add_pi(cls, data, file_elt):
        """Add processing instructions according to attributes dictionary.

        :type  data: class:`str` or :class:`lxml.etree.ElementTree`
        :param data:
            Name of file to transform or its content as a string or a tree.
        :type  file_elt: lxml.etree.Element
        :param file_elt: (optional)
            <file> XML element for the current file.
        """
        if not file_elt.attrib or isinstance(data, basestring):
            return

        # Find the way to select the right node (XPath or Xsl)
        select_elt = file_elt
        while select_elt is not None and select_elt.get('xslt') is None \
                and select_elt.get('xpath') is None:
            select_elt = select_elt.getparent()
        if select_elt is None or not select_elt.get('xpath'):
            return

        elts = []
        try:
            elts = data.xpath(select_elt.get('xpath'))
        except etree.XPathEvalError:
            return
        for elt in elts:
            for attr in file_elt.attrib:
                elt.insert(0, etree.ProcessingInstruction(
                    attr, file_elt.attrib[attr]))

    # -------------------------------------------------------------------------
    def _copy_templates(self, fid):
        """Copy processor, processing and pack templates into ``Output``
        directory.

        :param fid: (string, optional)
            File ID.
        :return: (boolean)
        """
        # Copy template files from INI files
        for name in self.config_list('Initialization', 'templates'):
            template = join(self.build.path, 'Processor', 'Templates', name)
            if not exists(template):
                self.build.stopped(
                    _('Template "${t}" does not exist', {'t': name}))
                return False
            path = self.config('template:%s' % name, 'path', '').format(
                fid=fid or '')
            copy_content(
                template, join(self.output, path), self._excluded_list(name),
                True)

        # Copy template files from processing and pack templates
        for name, path in self.build.processing['templates'] \
                + self.build.pack['templates']:
            template = join(self.build.data_path, name)
            if not exists(template):
                self.build.stopped(
                    _('Template "${t}" does not exist', {'t': name}))
                return False
            do_unzip = path[0:6] == 'unzip:'
            path = join(self.output, path[6:]) \
                if do_unzip else join(self.output, path)
            if isdir(template):
                copy_content(template, path, force=True)
            elif do_unzip and is_zipfile(template):
                unzip(template, path)
            else:
                if not exists(dirname(path)):
                    makedirs(dirname(path))
                copy(template, path)

        return True

    # -------------------------------------------------------------------------
    def _excluded_list(self, template):
        """Return exluded file list.

        :param template: (string)
            Template name.
        :return: (list)
        """
        exclude = []
        section = 'template:%s' % template
        if not self._config.has_section(section):
            return exclude

        for option in self._config.options(section):
            if option == 'exclude':
                exclude += self.config_list(section, option)
            elif option.startswith('exclude['):
                var_name = option[8:-1]
                if var_name[0] != '!' \
                        and self.build.processing['variables'].get(var_name):
                    exclude += self.config_list(section, option)
                elif var_name[0] == '!' and not \
                        self.build.processing['variables'].get(var_name[1:]):
                    exclude += self.config_list(section, option)

        return exclude

    # -------------------------------------------------------------------------
    def _remove_temporary_files(self, output, keep_dir=None):
        """Remove temporary files.

        :param output: (string)
            Absolute path to output directory.
        :param keep_dir: (string, optional)
            Name of directory to keep.
        """
        regex = re.compile(self.config(
            'Finalization', 'remove_regex', REMOVE_PATTERN))
        for path, dirs, files in walk(output, topdown=False):
            for name in dirs:
                if name != keep_dir and \
                   (regex.search(name) or not listdir(join(path, name))):
                    rmtree(join(path, name))
            for name in files:
                if regex.search(name):
                    remove(join(path, name))

        if exists(output) \
                and not samefile(output, join(self.build.path, 'Output')) \
                and not listdir(output):
            rmdir(output)
