"""Tests of ``lib.config`` classes and functions."""

from unittest import TestCase

from . import TEST_INI


# =============================================================================
class ConfigTestCase(TestCase):
    """Base class for testing config functions."""

    config = None

    # -------------------------------------------------------------------------
    def setUp(self):
        """Set up test application."""
        from os.path import dirname
        from configparser import ConfigParser

        self.config = ConfigParser({'here': dirname(TEST_INI)})
        self.config.read(TEST_INI)


# =============================================================================
class ULibConfigConfigGet(ConfigTestCase):
    """Unit test class for :func:`lib.config.config_get`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.config.config_get]"""
        from ..lib.config import config_get

        self.assertEqual(config_get(
            self.config, 'app:main', 'uid'), 'test')
        self.assertEqual(config_get(self.config, 'app:main', 'foo'), None)
        self.assertEqual(
            config_get(self.config, 'app:main', 'foo', 'bar'), 'bar')


# =============================================================================
class ULibConfigConfigGetList(ConfigTestCase):
    """Unit test class for :func:`lib.config.config_get_list`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.config.config_get_list]"""
        from ..lib.config import config_get_list

        self.assertEqual(
            config_get_list(self.config, 'app:main', 'uid'), ['test'])
        self.assertEqual(config_get_list(self.config, 'app:main', 'foo'), [])
        self.assertEqual(
            config_get_list(self.config, 'app:main', 'foo', 'bar'), 'bar')
        self.assertEqual(
            config_get_list(self.config, 'loggers', 'keys'),
            ['root', 'publiforge', 'sqlalchemy'])


# =============================================================================
class ULibConfigConfigGetNamespace(ConfigTestCase):
    """Unit test class for :func:`lib.config.config_get_namespace`."""

    # -------------------------------------------------------------------------
    def test_unknown_section(self):
        """[u:lib.config.config_get_namespace] unknown section"""
        from ..lib.config import config_get_namespace

        theme = config_get_namespace(self.config, 'foo', 'theme')
        self.assertEqual(len(theme), 0)

    # -------------------------------------------------------------------------
    def test_existing_section(self):
        """[u:lib.config.config_get_namespace] existing section"""
        from ..lib.config import config_get_namespace

        admin = config_get_namespace(self.config, 'Populate', 'admin')
        self.assertIn('login', admin)
        self.assertIn('password', admin)
        self.assertIn('name', admin)
        self.assertEqual(admin['login'], 'admin')


# =============================================================================
class ULibConfigSettingsGetList(TestCase):
    """Unit test class for :func:`lib.config.settings_get_list`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.config.settings_get_list]"""
        from ..lib.config import settings_get_list

        settings = {
            'option1': '',
            'option2': 'test',
            'option3': 'test1, test2'}
        self.assertEqual(settings_get_list(settings, 'option1'), [])
        self.assertEqual(settings_get_list(settings, 'optionX'), [])
        self.assertEqual(
            settings_get_list(settings, 'option1', ['vide']), ['vide'])
        self.assertEqual(
            settings_get_list(settings, 'optionX', ['vide']), ['vide'])
        self.assertEqual(
            settings_get_list(settings, 'option2'), ['test'])
        self.assertEqual(
            settings_get_list(settings, 'option3'), ['test1', 'test2'])


# =============================================================================
class ULibConfigSettingsGetDirectories(TestCase):
    """Unit test class for :func:`lib.config.settings_get_directories`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.config.settings_get_directories]"""
        from ..lib.config import settings_get_directories

        settings = {
            'processor.roots': 'publiforge:Processors, publiforge:Foo',
            'processor.list':  'Publi*, PackFilling, Parallel',
            'theme.default': 'Parallel'}
        directories = settings_get_directories(
            settings, 'processor', 'processor.xml')
        self.assertIn('Publidoc2Html5', directories)
        self.assertIn('Parallel', directories)
