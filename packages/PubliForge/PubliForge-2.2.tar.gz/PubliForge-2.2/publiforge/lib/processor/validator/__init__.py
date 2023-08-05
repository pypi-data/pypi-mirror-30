"""This module validates XML files against their Relax NG."""

import re
from os import walk
from os.path import join, exists, dirname, basename, isdir
from ConfigParser import ConfigParser

from ...i18n import _
from ...xml import load_xml
from ...processor import load_relaxngs


# =============================================================================
class Processor(object):
    """Main class for Validator processor."""

    # -------------------------------------------------------------------------
    def __init__(self, build):
        """Constructor method.

        :param build: (:class:`~.lib.build.agent.AgentBuild`)
            Main Build object.
        """
        # Attributes
        self.build = build

        # Configuration
        name = join(build.path, 'Processor', 'validator.ini')
        if not exists(name):
            build.stopped(_('File "validator.ini" is missing.'))
            return
        config = ConfigParser({'here': dirname(name)})
        config.optionxform = str
        config.read(name)

        # Relax NG
        self._relaxngs = load_relaxngs(self.build, config)
        if not self._relaxngs:
            build.stopped(_('No Relax NG.'))
            return

        # File selection
        self._file_regex = re.compile(config.get('Input', 'file_regex')) \
            if config.has_option('Input', 'file_regex') \
            else re.compile('\\.xml$')
        self._content_regex = config.has_option('Input', 'content_regex') \
            and re.compile(config.get('Input', 'content_regex'))

    # -------------------------------------------------------------------------
    def start(self):
        """Start the processor."""
        if self.build.stopped():
            return

        # Get file list
        file_list = []
        for filename in self.build.pack['files']:
            fullname = join(self.build.data_path, filename)
            if not exists(fullname):
                self.build.stopped('Unknown file "%s"' % filename, 'a_warn')
                continue
            if isdir(fullname):
                for path, ignored_, files in walk(fullname):
                    for name in files:
                        if not self._file_regex.search(name):
                            continue
                        name = join(path, name)
                        name = unicode(name.decode('utf8')) \
                            if isinstance(name, str) else name
                        file_list.append(name)
            elif self._file_regex.search(filename):
                file_list.append(fullname)
        if not file_list:
            self.build.stopped(_('nothing to do!'), 'a_error')
            return

        # Validate
        for count, name in enumerate(file_list):
            percent = 90 * (count + 1) / (len(file_list) + 1)
            self._validate(percent, name)

    # -------------------------------------------------------------------------
    def _validate(self, percent, filename):
        """Validate one XML file.

        :param percent: (integer)
            Percent of progress.
        :param filename: (string)
            Absolute path of the file to validate.
        """
        with open(filename, 'r') as hdl:
            data = hdl.read()
        if self._content_regex and not self._content_regex.search(data):
            return
        self.build.log(
            u'%s ............' % basename(filename), 'a_build', percent)
        data = load_xml(filename, self._relaxngs, data)
        if not isinstance(data, basestring):
            self.build.log(_('${f} is valid', {'f': basename(filename)}))
            return
        if 'values' not in self.build.result:
            self.build.result['values'] = []
        self.build.result['values'].append(data)
        self.build.stopped(data)
