"""Localization management."""

from os.path import dirname, join

from pyramid.i18n import TranslationStringFactory, make_localizer
from pyramid.exceptions import ConfigurationError

from .config import settings_get_list


_ = TranslationStringFactory('publiforge')


# =============================================================================
def locale_negotiator(request):
    """Locale negotiator to figure out the language to use.

    :type  request: pyramid.request.Request
    :param request:
        Current request.
    :rtype: str
    """
    if request.session.get('lang'):
        return request.session['lang']
    return request.accept_language.best_match(
        settings_get_list(
            request.registry.settings, 'languages', ['en']),
        request.registry.settings.get('pyramid.default_locale_name', 'en'))


# =============================================================================
def localizer(locale_name, directories=None):
    """Create a :class:`pyramid.i18n.Localizer` object corresponding to the
    provided locale name from the translations found in the list of translation
    directories.

    :param str locale_name:
        Current language.
    :param list directories: (optional)
        Translation directories.
    :rtype: pyramid.i18n.Localizer
    """
    return make_localizer(
        locale_name, directories or [join(dirname(__file__), '..', 'Locale')])


# =============================================================================
def add_translation_dirs(configurator, package):
    """Add one or more translation directory paths to the current configuration
    state according to settings and package name.

    :type  configurator: pyramid.config.Configurator
    :param configurator:
        Object used to do configuration declaration within the application.
    :param str package:
        Name of the calling package.
    """
    dirs = ['webbase:Locale', 'colander:locale']
    if package != 'webbase':
        dirs.insert(0, ('{0}:Locale'.format(package)))
    if configurator.get_settings().get('translation_dirs'):
        dirs = settings_get_list(
            configurator.get_settings(), 'translation_dirs') + dirs
    try:
        configurator.add_translation_dirs(*dirs)
    except (ImportError, ConfigurationError) as error:
        exit('*** Translation directories: {0}'.format(error))


# =============================================================================
def translate_field(request, i18n_fields):
    """Return the best translation according to user language.

    :type  request: pyramid.request.Request
    :param request:
        Current request.
    :param dict i18n_fields:
        Dictionary of avalaible translations.
    :rtype: str
    """
    if not i18n_fields:
        return ''
    return \
        'lang' in request.session and i18n_fields.get(request.session['lang'])\
        or i18n_fields.get(request.locale_name) \
        or i18n_fields.get(request.registry.settings.get(
            'pyramid.default_locale_name', 'en')) or ''
