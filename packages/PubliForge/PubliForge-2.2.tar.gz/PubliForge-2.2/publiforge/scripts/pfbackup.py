#!/usr/bin/env python
"""Backup site into a XML file."""

from logging import getLogger
from argparse import ArgumentParser
from os.path import exists
from locale import getdefaultlocale
from getpass import getuser
from sqlalchemy import engine_from_config
from sqlalchemy.exc import ProgrammingError
from webob import BaseRequest

from pyramid.paster import get_appsettings
from pyramid.threadlocal import get_current_registry
from pyramid.i18n import LocalizerRequestMixin

from ..lib.i18n import _, localizer
from ..lib.log import setup_logging
from ..lib.xml import export_configuration
from ..lib.build.agent import AgentBuildManager
from ..lib.build.front import FrontBuildManager
from ..models import DBSession, Base
from ..models.users import User
from ..models.groups import Group
from ..models.storages import Storage
from ..models.indexers import Indexer
from ..models.projects import Project


__credits__ = '(c) Prismallia http://www.prismallia.fr, 2010-2015'


LOG = getLogger(__name__)
DEFAULT_SETTINGS_NAME = 'PubliForge'


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = ArgumentParser(description='Backup site into a XML file.')
    parser.add_argument(
        'conf_uri', help='URI of configuration (e.g. pfinstance.ini#foo)')
    parser.add_argument('filename', help='name of backup file')
    parser.add_argument(
        '--log-level', dest='log_level', help='log level', default='INFO',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    parser.add_argument('--log-file', dest='log_file', help='log file')
    parser.add_argument(
        '--no-users', dest='no_users', help='no backup for users',
        action='store_true')
    parser.add_argument(
        '--no-groups', dest='no_groups', help='no backup for groups',
        action='store_true')
    parser.add_argument(
        '--no-storages', dest='no_storages', help='no backup for storages',
        action='store_true')
    parser.add_argument(
        '--no-index', dest='no_index', help='no backup for indexers',
        action='store_true')
    parser.add_argument(
        '--no-projects', dest='no_projects', help='no backup for projects',
        action='store_true')
    args = parser.parse_args()
    if not exists(args.conf_uri.partition('#')[0]):
        parser.print_usage()
        return
    setup_logging(args.log_level, args.log_file)

    # Backup
    Backup(args).save(args.conf_uri, args.filename)


# =============================================================================
class Backup(object):
    """Class to backup site."""

    # -------------------------------------------------------------------------
    def __init__(self, args):
        """Constructor method."""
        self._args = args

    # -------------------------------------------------------------------------
    def save(self, conf_uri, filename):
        """Save asked elements.

        :param conf_uri: (string)
            Configuration file of the instance.
        :param filename: (string)
            Name of backup file.
        :return: (boolean)
        """
        # Read configuration file
        settings = get_appsettings(conf_uri)
        if len(settings) < 3:
            try:
                settings = get_appsettings(conf_uri, DEFAULT_SETTINGS_NAME)
            except LookupError:
                pass
        if 'uid' not in settings or 'sqlalchemy.url' not in settings:
            LOG.critical(localizer(getdefaultlocale()[0]).translate(_(
                'Incorrect configuration file "${f}".', {'f': conf_uri})))
            return False

        # Initialize SqlAlchemy session
        dbengine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=dbengine)
        Base.metadata.bind = dbengine
        try:
            DBSession.query(User).first()
        except ProgrammingError:
            LOG.warning(localizer(
                getdefaultlocale()[0]).translate(_('Database is empty!')))
            DBSession.close()
            DBSession.remove()
            return True

        # Browse elements
        elements = self._get_elements(settings)

        # Export configuration
        if elements:
            export_configuration(elements, filename, True)
        else:
            LOG.warning(localizer(
                getdefaultlocale()[0]).translate(_('Nothing to do!')))
        DBSession.close()
        DBSession.remove()
        return True

    # -------------------------------------------------------------------------
    def _get_elements(self, settings):
        """Get all XML elements of the configuration.

        :param settings: (dictionary)
            Settings dictionary.
        :return: (list)
        """
        elements = []

        if not hasattr(self._args, 'no_users') or not self._args.no_users:
            for user in DBSession.query(User).order_by('login'):
                elements.append(user.xml(True))

        if not hasattr(self._args, 'no_groups') or not self._args.no_groups:
            for group in DBSession.query(Group).order_by('group_id'):
                elements.append(group.xml())

        if not hasattr(self._args, 'no_storages') \
                or not self._args.no_storages:
            for storage in DBSession.query(Storage).order_by('storage_id'):
                elements.append(storage.xml())

        if not hasattr(self._args, 'no_index') or not self._args.no_index:
            for group in DBSession.query(Indexer).order_by('indexer_id'):
                elements.append(group.xml())

        if not hasattr(self._args, 'no_projects') \
                or not self._args.no_projects:
            request = DummyRequest(settings)
            for project in DBSession.query(Project).order_by('label'):
                elements.append(project.xml(request))

        return [k for k in elements if k is not None]


# =============================================================================
class DummyRequest(BaseRequest, LocalizerRequestMixin):
    """Dummy request for processors."""
    # pylint: disable = too-few-public-methods

    # -------------------------------------------------------------------------
    def __init__(self, settings):
        """Constructor method."""
        self.environ = {}
        super(DummyRequest, self).__init__(self.environ)
        self.registry = get_current_registry()
        self.registry['abuild'] = AgentBuildManager(settings)
        self.registry['fbuild'] = FrontBuildManager(settings)
        self.registry.settings = settings
        self.session = {
            'user_id': 0, 'login': getuser(), 'lang': getdefaultlocale()[0],
            'name': getuser()}


# =============================================================================
if __name__ == '__main__':
    main()
