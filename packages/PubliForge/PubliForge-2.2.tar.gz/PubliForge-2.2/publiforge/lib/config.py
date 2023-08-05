"""Various functions to parse configuration files or settings."""

from sys import version_info
from os import listdir
from os.path import exists, join, normpath
from fnmatch import fnmatch

from pyramid.asset import abspath_from_asset_spec


# =============================================================================
def config_get(config, section, option, default=None):
    """Retrieve a value from a configuration object.

    :type  config: configparser.ConfigParser
    :param config:
        Configuration object.
    :param str section:
        Section name.
    :param str option:
        Option name.
    :param str default: (optional)
        Default value
    :rtype: str
        Read value or default value.
    """
    if not config.has_option(section, option):
        return default
    value = config.get(section, option)
    if version_info > (3, 0):
        return value or None  # pragma: no cover
    return value.decode('utf8') if isinstance(value, str) \
        else value  # pragma: no cover


# =============================================================================
def config_get_list(config, section, option, default=None):
    """Retrieve a list of values from a configuration object.

    :type  config: configparser.ConfigParser
    :param config:
        Configuration object.
    :param str section:
        Section name.
    :param str option:
        Option name.
    :param list default: (optional)
        Default values.
    :rtype: list
    """
    if not config.has_option(section, option):
        return default or []
    values = config_get(config, section, option)
    return [k.strip() for k in values.split(',')] if values else []


# =============================================================================
def config_get_namespace(config, section, namespace):
    """Retrieve all options beginning by a name space.

    :type  config: configparser.ConfigParser
    :param config:
        Configuration object.
    :param str section:
        Section name.
    :param str namespace:
        Prefix of options to retrieve.
    :rtype: dict
    """
    values = {}
    ns_len = len(namespace) + 1
    if not config.has_section(section):
        return values

    for option in config.options(section):
        if option.startswith('%s.' % namespace):
            values[option[ns_len:].replace('.', '_')] = config_get(
                config, section, option)
    return values


# =============================================================================
def settings_get_list(settings, option, default=None):
    """Retrieve a list of values from a settings dictionary.

    :type  settings: pyramid.registry.Registry.settings
    :param settings:
        Settings object.
    :param str option:
        Option name.
    :param list default: (optional)
        Default values.
    :rtype: list
    """
    if not settings.get(option):
        return default or []
    return [k.strip() for k in settings[option].split(',')]


# =============================================================================
def settings_get_directories(settings, namespace, conf_file):
    """Retrieve all directories whose root is contained in one of the
    directories listed in ``namespace.roots``, name matches one of the patterns
    listed in ``namespace.patterns`` and containing the file ``filename``.

    :type  settings: pyramid.registry.Registry.settings
    :param settings:
        Settings object.
    :param str namespace:
        Prefix of options to retrieve.
    :param str namespace:
        Prefix of options to retrieve.
    :param str conf_file:
        Name of configuration file to search in each directory.
    :rtype: dict
    """
    directories = {}
    done = set()
    patterns = settings_get_list(settings, '%s.list' % namespace, '')
    for root in settings_get_list(settings, '%s.roots' % namespace, ''):
        root = normpath(abspath_from_asset_spec(root))
        if root in done or not exists(root):
            continue
        for directory in listdir(root):
            if not exists(join(root, directory, conf_file)):
                continue
            for pattern in patterns:
                if fnmatch(directory, pattern):
                    directories[directory] = join(root, directory)
                    break

    return directories
