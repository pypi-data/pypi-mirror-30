"""This module makes Publiset XML file from a pack structure."""

import fnmatch
import re
from os import makedirs, walk, listdir, remove, rmdir
from os.path import join, exists, dirname, isdir, relpath, samefile, basename
from ConfigParser import ConfigParser
from shutil import rmtree
from lxml import etree

from ...i18n import _
from ...config import config_get, config_get_list
from ...utils import normalize_spaces, make_id, camel_case
from ...xml import PUBLIFORGE_RNG_VERSION, load_xml
from .. import load_relaxngs
from ..leprisme.transform import Transform
from ..leprisme.publiset import Publiset


# =============================================================================
class Processor(object):
    """Main class for Publiseter processor."""

    # -------------------------------------------------------------------------
    def __init__(self, build):
        """Constructor method.

        :param build: (:class:`~.lib.build.agent.AgentBuild`)
            Main Build object.
        """
        # Attributes
        self.percents = [1, 90]
        self.build = build
        self.output = join(self.build.path, 'Output')

        # Configuration
        name = join(build.path, 'Processor', 'publiseter.ini')
        if not exists(name):
            build.stopped(_('File "publiseter.ini" is missing.'))
            return
        self._config = ConfigParser({'here': dirname(name), 'fid': '{fid}'})
        self._config.read(name)

        # Relax NG
        self.relaxngs = load_relaxngs(self.build, self._config)

        # Transformation
        self._transform = Transform(self, [''])

    # -------------------------------------------------------------------------
    def start(self):
        """Start the processor."""
        if self.build.stopped():
            return

        # Publiset ID
        fid = make_id(
            self.build.processing['variables'].get('id'), 'token')
        if not fid:
            fid = make_id(self.build.pack['label'], 'token')

        # Update output
        subdir = self.build.processing['variables'].get('subdir')
        if subdir:
            self.output = join(
                self.build.path, 'Output',
                subdir.replace('%(fid)s', camel_case(fid)))
        else:
            self.output = join(self.build.path, 'Output')

        # Create directories
        for name in config_get_list(
                self._config, 'Initialization', 'directories'):
            if not exists(join(self.output, name)):
                makedirs(join(self.output, name))

        # Transform pack into Publiset
        self._transform.start('%s.xml' % fid, fid, self._create_pack())

        # Transform Publiset
        if self.build.processing['variables'].get('assembly'):
            self._assembly(fid)

        # Clean up
        self.finalize(True)

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
    def finalize(self, force=False):
        """Finalization."""
        if not force or self.build.processing['variables'].get('keeptmp'):
            return
        regex = self.config(
            'Finalization', 'remove_regex', r'(~|\.tmp)(\.\w{1,4})?$')
        for path, dirs, files \
                in walk(join(self.build.path, 'Output'), topdown=False):
            for name in dirs:
                if (regex and re.search(regex, name)) \
                        or not listdir(join(path, name)):
                    rmtree(join(path, name))
            for name in files:
                if regex and re.search(regex, name):
                    remove(join(path, name))

        if exists(self.output) \
                and not samefile(self.output, join(self.build.path, 'Output'))\
                and not listdir(self.output):
            rmdir(self.output)

    # -------------------------------------------------------------------------
    def _create_pack(self):
        """Create the XML pack.

        :return: (:class:`lxml.etree.Element` instance)
        """
        root = etree.Element('publiforge', version=PUBLIFORGE_RNG_VERSION)
        pack_elt = etree.SubElement(root, 'pack')
        etree.SubElement(pack_elt, 'label').text = \
            normalize_spaces(self.build.pack['label'])
        files_elt = etree.SubElement(pack_elt, 'files')

        prefix = None
        if not self.build.processing['variables'].get('assembly'):
            prefix = '%s-' % camel_case(self.build.context['front_id'])
        excluded = self.build.processing['variables'].get('file_exclude')
        excluded = re.compile(excluded) if excluded else None
        included = self.build.processing['variables'].get('file_include')
        included = re.compile(included) if included else None

        for filename in self.build.pack['files']:
            fullname = join(self.build.data_path, filename)
            if isdir(fullname) and self.build.pack['recursive']:
                for path, ignored_, files in walk(fullname):
                    for name in sorted(fnmatch.filter(files, '*.xml')):
                        if not self._keep_it(excluded, included, name):
                            continue
                        name = relpath(join(path, name), self.build.data_path)
                        name = name.partition(prefix)[2] if prefix else name
                        name = name if isinstance(name, unicode) \
                            else name.decode('utf8')
                        etree.SubElement(files_elt, 'file').text = name
            elif isdir(fullname):
                for name in sorted(fnmatch.filter(listdir(fullname), '*.xml')):
                    if not self._keep_it(excluded, included, name):
                        continue
                    name = relpath(join(fullname, name), self.build.data_path)
                    name = name.partition(prefix)[2] if prefix else name
                    name = name if isinstance(name, unicode) \
                        else name.decode('utf8')
                    etree.SubElement(files_elt, 'file').text = \
                        name.decode('utf8')
            elif self._keep_it(excluded, included, basename(filename)):
                etree.SubElement(files_elt, 'file').text = \
                    filename.partition(prefix)[2] if prefix else filename

        return root

    # -------------------------------------------------------------------------
    def _assembly(self, fid):
        """Realize the assembly.

        :param fid: (string)
            Publiset file ID.
        """
        # Load the Publiset
        # pylint: disable = E1103
        root = load_xml(join(
            self.output, self.config('Output', 'format', '').format(fid=fid)))
        if isinstance(root, basestring):
            self.build.stopped(root)
            return

        # Process
        data_path = join(
            self.build.data_path, self.build.processing['variables']
            .get('div1_path', '').replace('..', '-'))
        publiset = Publiset(self, data_path)
        set_root = root.find('composition')
        if set_root is None:
            self.build.stopped(_('Empty composition!'))
            return
        self.build.log(_('${f}: document composition', {'f': fid}))
        self._transform.start(
            '%s.xml' % fid, fid, publiset.compose('%s.xml' % fid, set_root))

    # -------------------------------------------------------------------------
    @classmethod
    def _keep_it(cls, excluded, included, filename):
        """Check if the file ``filename`` is kept according to ``excluded`` and
        ``included``.

        :param excluded: (:class:`re` object)
            Regular expression to define file to exclude.
        :param included: (:class:`re` object)
            Regular expression to define file to include.
        :param filename: (string)
            Name of file to check.
         :return: (boolean)
        """
        if excluded and excluded.search(filename):
            return False
        if included and not included.search(filename):
            return False
        return True
