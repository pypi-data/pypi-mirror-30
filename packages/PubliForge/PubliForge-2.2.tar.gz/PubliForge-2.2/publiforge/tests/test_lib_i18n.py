# -*- coding: utf-8 -*-
"""Tests of ``lib.i18n`` functions."""

from unittest import TestCase

from pyramid import testing


# =============================================================================
class ULibI18nLocaleNegotiator(TestCase):
    """Unit test class for :func:`lib.i18n.locale_negotiator`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.i18n.locale_negotiator]"""
        from webob.acceptparse import AcceptLanguage
        from ..lib.i18n import locale_negotiator

        request = testing.DummyRequest(accept_language=AcceptLanguage(
            'fr-FR, fr;q=0.8, en-US;q=0.5, en;q=0.3'))
        request.registry.settings = {}
        language = locale_negotiator(request)
        self.assertEqual(language, 'en')

        request.session['lang'] = 'fr'
        language = locale_negotiator(request)
        self.assertEqual(language, 'fr')


# =============================================================================
class ULibI18nLocalizer(TestCase):
    """Unit test class for :func:`lib.i18n.localizer`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.i18n.localizer]"""
        from pyramid.i18n import Localizer
        from ..lib.i18n import localizer

        self.assertIsInstance(localizer('fr'), Localizer)


# =============================================================================
class ULibI18nAddTranslationDirs(TestCase):
    """Unit test class for :func:`lib.i18n.add_translation_dirs`."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Set up test application."""
        self.configurator = testing.setUp(settings={})

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects of ``pyramid.testing.setUp()``."""
        testing.tearDown()

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.i18n.add_translation_dirs]"""
        from ..lib.i18n import add_translation_dirs

        add_translation_dirs(self.configurator, 'webbase')
        self.assertRaises(
            SystemExit, add_translation_dirs, self.configurator, 'foo')

        self.configurator.get_settings()['translation_dirs'] = 'bar'
        self.assertRaises(
            SystemExit, add_translation_dirs, self.configurator, 'foo')


# =============================================================================
class ULibI18nTranslateField(TestCase):
    """Unit test class for :func:`lib.i18n.translate_field`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.i18n.translate_field]"""
        from pyramid.testing import DummyRequest
        from ..lib.i18n import translate_field

        request = DummyRequest()
        self.assertEqual(translate_field(request, None), '')

        i18n_field = {'en': 'User editor', 'fr': u'Éditeur des utilisateurs'}
        self.assertEqual(translate_field(request, i18n_field), 'User editor')

        request.locale_name = 'fr'
        self.assertEqual(
            translate_field(request, i18n_field), u'Éditeur des utilisateurs')

        request.locale_name = 'en'
        request.session['lang'] = 'fr'
        self.assertEqual(
            translate_field(request, i18n_field), u'Éditeur des utilisateurs')

        request.locale_name = 'es'
        request.session['lang'] = 'es'
        self.assertEqual(translate_field(request, i18n_field), 'User editor')
