"""Various functions to manage logs."""

from logging import getLogger, basicConfig
from os import makedirs
from os.path import expanduser, dirname, exists
from configparser import ConfigParser

from .config import config_get_list


LOG_ACTIVITY = getLogger('activity')


# =============================================================================
def setup_logging(log_level='INFO', log_file=None, log_format=None):
    """Initialize logging system.

    :param str log_level: ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        Log level. By default `INFO`.
    :param str log_file: (optional)
        Path to log file.
    :param str log_format: (optional)
        Format for log entry. By default,
        `%(asctime)s %(levelname)-8s %(message)s`
    """
    if log_format is None:
        log_format = '%(asctime)s %(levelname)-8s %(message)s'
    if log_file:
        basicConfig(
            filename=expanduser(log_file), filemode='w', level=log_level,
            format=log_format)
    else:
        basicConfig(level=log_level, format=log_format)


# =============================================================================
def log_activity_setup(global_config):
    """Create log directory.

    :param dict global_config:
        Dictionary describing the INI file with keys ``__file__`` and ``here``.
    :rtype: bool
    :return:
        Return ``True`` if activity log is activated.
    """
    config = ConfigParser({'here': global_config['here']})
    config.read(global_config['__file__'])
    if 'activity' not in config_get_list(config, 'loggers', 'keys') or \
       not config.has_option('handler_activity', 'args'):
        return False

    # pylint: disable = eval-used
    log_args = eval(config.get('handler_activity', 'args'))
    path = dirname(log_args[0])
    if not exists(path):
        makedirs(path)
    return True


# =============================================================================
def log_activity(request, action, *args):
    """Write a message in the activity log.

    :type  request: pyramid.request.Request
    :param request:
        Current request.
    :param str action:
        Action in action.
    :param list args:
        Non-keyworded arguments.
    """
    if request.registry.get('log_activity'):
        LOG_ACTIVITY.info(
            u'[%s] %s %s',
            (hasattr(request, 'session') and request.session.get('login')) or
            ('context' in request.registry and
             request.registry['context'].get('login')) or '',
            action, u' '.join(args))


# =============================================================================
def log_error(request, error):
    """Write an error message in the log.

    :type  request: pyramid.request.Request
    :param request:
        Current request.
    """
    if request.registry.get('log_activity'):
        LOG_ACTIVITY.error(
            u'[%s] %s',
            (hasattr(request, 'session') and request.session.get('login')) or
            ('context' in request.registry and
             request.registry['context'].get('login')) or '', error)
