"""XML Transformation via XSL stylesheet."""

import re
import fnmatch
from os import walk, remove, makedirs
from os.path import exists, join, dirname, basename, relpath, splitext, isdir
from imp import load_source
from lxml import etree

from ...i18n import _
from ...utils import load_regex, make_id
from ...xml import PF_NAMESPACE, load_xml
from ...xml import xpath_camel_case, xpath_make_id, xpath_relpath, xpath_wrap
from . import containers
from .iniscript import IniScript


TMP_SUFFIX = {
    'start': '0start', 'preprocess': '1process', 'preregex': '2regex',
    'xslt': '3xslt', 'postregex': '4regex', 'postini': '5postini',
    'postprocess': '6process'}


# =============================================================================
class Transform(object):
    """Class for XML transformation."""
    # pylint: disable = E1103, R0902

    # -------------------------------------------------------------------------
    def __init__(self, processor, steps):
        """Constructor method.

        :param processor: (:class:`~.lib.processor.leprisme.Processor` object)
            Processor object on which it depends.
        """
        self._processor = processor
        self._steps = steps
        self.fid = None
        self.data = None

        # Load scripts, regex and XSL
        self._scripts = self._load_scripts()
        self._regex = self._load_regex()
        self._xslt = self._load_xslt()
        self._xml_decl = None
        namespace = etree.FunctionNamespace(PF_NAMESPACE)
        namespace['camel_case'] = xpath_camel_case
        namespace['make_id'] = xpath_make_id
        namespace['relpath'] = xpath_relpath
        namespace['wrap'] = xpath_wrap

        # List container factories
        self._factories = {
            'Zip': containers.ZipFactory(processor),
            'OCF': containers.OcfFactory(processor)}

        # INI script
        self._iniscript = IniScript(processor)

    # -------------------------------------------------------------------------
    def start(self, filename, fid, data):
        """Start the transformation.

        :param str filename:
            Relative path to the original file to transform.
        :param str fid:
            File ID.
        :type  data: class:`str` or :class:`lxml.etree.ElementTree`
        :param data:
            Name of file to transform or its content as a string or a tree.
        """
        # pylint: disable = R0911
        # Initialization
        if data is None or self._processor.build.stopped():
            return
        self._xml_decl = None
        self.fid = fid
        self.data = data
        self._save_tmp('-%s' % TMP_SUFFIX['start'])
        percent_delta = \
            (self._processor.percents[1] - self._processor.percents[0]) \
            / (11 * len(self._steps) + 1)

        for index, step in enumerate(self._steps):
            # Preprocess
            self._script_transform(
                step, 'preprocess', filename, 2 * percent_delta)
            self._processor.percents[0] += 2 * percent_delta

            # Pre regex transformation
            self._regex_transform(step, 'preregex')
            self._processor.percents[0] += percent_delta

            # XSL transformation & INI media files execution
            self._xsl_transform(
                index, step, self._processor.build.processing['variables'])
            self._processor.percents[0] += percent_delta
            self._media_iniscripts(step, filename, 2 * percent_delta)
            self._processor.percents[0] += 2 * percent_delta

            # Post regex transformation
            self._regex_transform(step, 'postregex')
            self._processor.percents[0] += percent_delta

            # Postprocess
            self._post_iniscript(step)
            self._processor.percents[0] += 2 * percent_delta
            self._script_transform(
                step, 'postprocess', filename, 2 * percent_delta)
            self._processor.percents[0] += 2 * percent_delta

        # Finalize
        self._finalize()

    # -------------------------------------------------------------------------
    def _load_scripts(self):
        """Load transformation script files.

        :return: (dictionary)
            A dictionary of script main functions.
         """
        scripts = {}
        for step in self._steps:
            for kind in ('preprocess', 'postprocess'):
                filename = self._processor.config(
                    'Transformation%s' % step, kind)
                if not filename:
                    continue
                if not exists(filename):
                    self._processor.build.stopped(
                        _('Unknown file "${n}".', {'n': filename}))
                    continue
                module = load_source(splitext(basename(filename))[0], filename)
                scripts['%s:%s' % (step, kind)] = module.main

        return scripts

    # -------------------------------------------------------------------------
    def _load_regex(self):
        """Load regular expressions from files.

        :return: (dictionary)
            A dictionary of 2 tuples of regular expressions.
        """
        regex = {}
        for step in self._steps:
            for kind in ('preregex', 'postregex'):
                kind_regex = []
                for filename in self._processor.config_list(
                        'Transformation%s' % step, kind, []):
                    if not exists(filename):
                        self._processor.build.stopped(
                            'Unknown file "%s".' % filename)
                        continue
                    kind_regex += load_regex(filename)
                if kind_regex:
                    regex['%s:%s' % (step, kind)] = tuple(kind_regex)
        return regex

    # -------------------------------------------------------------------------
    def _load_xslt(self):
        """Load XSL file and create a etree.XSLT object.

        :return: (dictionary)
            A dictionary of :class:`lxml.etree.XSLT` instances.
        """
        xslt = {}
        for step in self._steps:
            filename = self._processor.config('Transformation%s' % step, 'xsl')
            if not filename:
                continue
            try:
                xslt[step] = etree.XSLT(etree.parse(filename))
            except (IOError, etree.XSLTParseError,
                    etree.XMLSyntaxError) as err:
                self._processor.build.stopped(
                    str(err).replace(self._processor.build.path, '..'))
                continue

        return xslt

    # -------------------------------------------------------------------------
    def _script_transform(self, step, kind, filename, delta):
        """Customized script transformation.

        :param step: (string)
            Current ``[Transformation]`` section suffix.
        :param kind: ('preprocess' or 'postprocess')
            Kind of regular expressions.
        :param filename: (string)
            Relative path to file to transform.
        :param delta: (integer)
            Delta for percent of progress for this method.
        """
        name = '%s:%s' % (step, kind)
        if name not in self._scripts or self.data is None \
                or self._processor.build.stopped():
            return
        message = {'f': self.fid, 's': step}
        message = {
            'preprocess': _('${f}: preprocess ${s}', message),
            'postprocess': _('${f}: post process ${s}', message)}\
            .get(kind, '%s: %s %s' % (self.fid, step, kind))
        self._processor.build.log(
            message, step='a_build', percent=self._processor.percents[0])
        percent_limit = self._processor.percents[1]
        self._processor.percents[1] = self._processor.percents[0] + delta
        self.data = self._scripts[name](
            self._processor, filename, self.fid, self.data)
        self._processor.percents[1] = percent_limit
        if self.data is not None:
            self._save_tmp('%s-%s' % (step, TMP_SUFFIX[kind]))

    # -------------------------------------------------------------------------
    def _regex_transform(self, step, kind):
        """Regular expression transformation.

        :param step: (string)
            Current ``[Transformation]`` section suffix.
        :param kind: ('preregex' or 'postregex')
            Kind of regular expressions.
        :return: (string)
            Modified data or ``None`` if fails.
        """
        name = '%s:%s' % (step, kind)
        file_regex = self._processor.config(
            'Transformation%s' % step, '%s.files' % kind)
        file_regex = file_regex and file_regex.replace('{fid}', self.fid)
        if name not in self._regex or (not self.data and not file_regex) \
                or self._processor.build.stopped():
            return
        message = {'f': self.fid, 's': step}
        message = {
            'preregex': _('${f}: pre-regex ${s}', message),
            'postregex': _('${f}: post regex ${s}', message)}\
            .get(kind, '%s: %s %s' % (self.fid, step, kind))
        self._processor.build.log(
            message, step='a_build', percent=self._processor.percents[0])

        # Transform main data
        if self.data:
            # Possibly, convert data into string
            if not isinstance(self.data, basestring):
                self.data = etree.tostring(
                    self.data, encoding='utf-8',
                    xml_declaration=self._xml_decl, pretty_print=True)

            # Transform
            self.data = self.data.decode('utf8')
            for regex in self._regex[name]:
                try:
                    self.data = regex[0].sub(regex[1], self.data)
                except re.error as error:
                    self.data = self.data.encode('utf8')
                    self._processor.build.stopped(
                        '%s: %s' % (regex[0].pattern, error))
                    return
            self.data = self.data.encode('utf8')
            self._save_tmp('%s-%s' % (step, TMP_SUFFIX[kind]))

        # Transform other files
        if file_regex:
            file_regex = re.compile(file_regex)
            for path, ignored_, files in walk(self._processor.output):
                for filename in files:
                    if file_regex.search(filename):
                        filename = join(path, filename)
                        with open(filename, 'r') as hdl:
                            data = hdl.read().decode('utf8')
                        for regex in self._regex[name]:
                            data = regex[0].sub(regex[1], data)
                        data = data.encode('utf8')
                        with open(filename, 'w') as hdl:
                            hdl.write(data)

    # -------------------------------------------------------------------------
    def _xsl_transform(self, index, step, variables):
        """XSL transformation.

        :param int index:
            Index of th current step.
        :param str step:
            Current ``[Transformation]`` section suffix.
        :param dict variables:
            Variable dictionary for XSL.
        """
        if step not in self._xslt or self.data in (None, '') \
                or self._processor.build.stopped():
            return
        self._processor.build.log(
            _('${f}: XSL transformation ${s}', {'f': self.fid, 's': step}),
            step='a_build', percent=self._processor.percents[0])

        # Possibly, load XML
        if isinstance(self.data, basestring):
            relaxngs = not index \
                and self._processor.config('Input', 'validate') == 'true' \
                and self._processor.relaxngs or None
            self.data = load_xml(self.fid, relaxngs, self.data)
            if isinstance(self.data, basestring):
                self._processor.build.stopped(self.data, 'a_error')
                self.data = None
                return

        # Create params dictionary
        params = {
            'fid': '"%s"' % self.fid,
            'output': '"%s/"' % self._processor.output,
            'processor':
            '"%s/"' % join(self._processor.build.path, 'Processor')}
        for name, value in variables.items():
            if isinstance(value, bool):
                params[name] = str(int(value))
            elif isinstance(value, int):
                params[name] = str(value)
            else:
                params[name] = '"%s"' % value

        # Transform
        if not exists(self._processor.output):
            makedirs(self._processor.output)
        errors = len(self._xslt[step].error_log)
        try:
            self.data = self._xslt[step](self.data, **params)
        except etree.XSLTApplyError as err:
            self._processor.build.stopped(err)
            return

        # Read the result
        for err, error in enumerate(self._xslt[step].error_log):
            if err >= errors:
                if 'values' not in self._processor.build.result:
                    self._processor.build.result['values'] = []
                self._processor.build.result['values'].append(error.message)
        self._xml_decl = '<?xml ' in str(self.data)
        self.data = etree.ElementTree(self.data.getroot()) \
            if self.data.getroot() is not None else str(self.data)

        self._save_tmp('%s-%s' % (step, TMP_SUFFIX['xslt']))

    # -------------------------------------------------------------------------
    def _media_iniscripts(self, step, filename, delta):
        """Browse generated INI files for media and process them.

        :param step: (string)
            Current ``[Transformation]`` section suffix.
        :param filename: (string)
            Relative path to the original file to transform.
        :param delta: (integer)
            Delta for percent of progress for this method.
        """
        if self._processor.build.stopped():
            return

        # Total of INI files to process
        count = total = 0
        for path, ignored_, files in walk(self._processor.output):
            for name in fnmatch.filter(files, '%s-*~.ini' % self.fid):
                total += 1
        if not total:
            return

        # Process
        done_tag = make_id(step, 'token')
        success = True
        for path, ignored_, files in walk(self._processor.output):
            for name in sorted(fnmatch.filter(files, '%s-*~.ini' % self.fid)):
                success &= self._iniscript.convert_media(
                    filename, join(path, name), done_tag,
                    self._processor.percents[0] + delta * count / total)
                count += 1
                if self._processor.build.stopped():
                    break
        if not success:
            self._processor.build.stopped(_(
                '${f}: a media is missing', {'f': self.fid}), level='a_error')

    # -------------------------------------------------------------------------
    def _post_iniscript(self, step):
        """Look for post INI script and process it.

        :param step: (string)
            Current ``[Transformation]`` section suffix.
        """
        # Something to do?
        if self._processor.build.stopped():
            return
        fmt = self._processor.config('Output', 'format', '')
        target_file = \
            join(self._processor.output, unicode(fmt).format(fid=self.fid))
        ini_file = join(self._processor.output, '%s~.ini' % self.fid)
        if not exists(ini_file):
            return

        # Execution
        self._processor.build.log(
            _('${f}: post script ${s}', {'f': self.fid, 's': step}),
            step='a_build', percent=self._processor.percents[0])
        self._save_data(fmt)
        self._iniscript.post_execution(
            ini_file, target_file, make_id(step, 'token'))

        # Reload data
        if exists(target_file) and not isdir(target_file):
            with open(target_file, 'r') as hdl:
                self.data = hdl.read()
        self._save_tmp('%s-%s' % (step, TMP_SUFFIX['postini']))

    # -------------------------------------------------------------------------
    def _save_tmp(self, suffix):
        """Save temporary data on file to debug.

        :param suffix: (string)
            Suffix for temporary file name.
        """
        if self._processor.build.processing['variables'].get('keeptmp'):
            fmt = '{fid}%s~.%s' % (
                make_id(suffix, 'token'),
                'txt' if isinstance(self.data, basestring) else 'xml')
            self._save_data(fmt)

    # -------------------------------------------------------------------------
    def _save_data(self, fmt):
        """Save data on file.

        :param fmt: (string)
            Target name format.
        :return: (string)
            Full path to saved file.
        """
        # Nothing to save
        if self.data is None or not fmt:
            return None

        # File name and directory
        filename = join(
            self._processor.output, unicode(fmt).format(fid=self.fid))
        if not exists(dirname(filename)):
            makedirs(dirname(filename))

        # Save string
        if isinstance(self.data, basestring):
            if not self.data.strip() or isdir(filename):
                return None
            with open(filename, 'w') as hdl:
                hdl.write(self.data)
        # Save XML/HTML file
        elif not isdir(filename):
            try:
                content = etree.tostring(
                    self.data, encoding='utf-8',
                    xml_declaration=self._xml_decl, pretty_print=True)
            except (ValueError, AssertionError, AttributeError) as err:
                self._processor.build.stopped(err, 'a_error')
                return None
            with open(filename, 'w') as hdl:
                hdl.write(content)

        return filename

    # -------------------------------------------------------------------------
    def _finalize(self):
        """Finalization."""
        build = self._processor.build
        build.log(
            _('${f}: finalization', {'f': self.fid}),
            step='a_build', percent=self._processor.percents[0])

        # Save file
        fmt = self._processor.config('Output', 'format', '')
        filename = self._save_data(fmt) \
            or join(self._processor.output, unicode(fmt).format(fid=self.fid))
        if not fmt or not exists(filename):
            filename = None
        if build.stopped():
            return

        # Validation
        # pylint: disable = too-many-boolean-expressions
        if filename is not None and self.data not in (None, '') \
           and self._processor.relaxngs is not None \
           and (('validate' in build.processing['variables'] and
                 build.processing['variables']['validate']) or
                ('validate' not in build.processing['variables'] and
                 self._processor.config('Output', 'validate') == 'true')):
            self.data = load_xml(filename, self._processor.relaxngs, self.data)
            if isinstance(self.data, basestring):
                build.stopped(self.data, 'a_error')
                remove(filename)
                return

        # Backup in attic
        build.output2attic()

        # Container
        fmt, filename = self._make_container(filename)
        if not fmt:
            return

        # Main finalization
        if build.processing['variables'].get('subdir'):
            self._processor.finalize()

        # Update result
        if not build.stopped():
            self._update_result(filename)

    # -------------------------------------------------------------------------
    def _update_result(self, filename):
        """Update result dictionary during finalization.

        :param filename: (string)
        """
        build = self._processor.build
        if filename is not None:
            filename = relpath(filename, join(build.path, 'Output'))
            if 'files' not in build.result:
                build.result['files'] = []
            if filename not in build.result['files']:
                build.result['files'].append(filename)
        elif isinstance(self.data, basestring) and self.data.strip():
            if 'values' not in build.result:
                build.result['values'] = []
            build.result['values'].append(self.data.decode('utf8'))
        elif isinstance(self.data, list) and self.data:
            if 'values' not in build.result:
                build.result['values'] = []
            for value in self.data:
                build.result['values'].append(value)

    # -------------------------------------------------------------------------
    def _make_container(self, filename):
        """If necessary, create the container (ZIP, OCF...).

        :param filename: (string)
        :return: (tuple)
        """
        processor = self._processor
        container = processor.config('Output', 'container') or \
            (processor.build.processing['variables'].get('zip') and 'Zip') \
            or None
        if container is None:
            return True, filename
        if container not in self._factories:
            processor.build.stopped(
                _('Unknown container "${c}"', {'c': container}))
            return False, filename

        processor.build.log(
            _('${f}: container ${c}', {'f': self.fid, 'c': container}),
            'a_build', processor.percents[0])
        filename = self._factories[container].make(self.fid, processor.output)

        return bool(filename), filename
