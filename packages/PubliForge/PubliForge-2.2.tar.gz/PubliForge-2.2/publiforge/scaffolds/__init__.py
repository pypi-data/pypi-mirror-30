"""PubliForge scaffolds."""

from sys import stdin, version_info
from os.path import join
from textwrap import dedent
from builtins import input as cmdline_input
from base64 import b64encode
from hashlib import sha1

from pyramid.scaffolds import PyramidTemplate

from ..lib.utils import make_id, token, email_is_valid, normalize_spaces
from ..lib.utils import camel_case
from ..lib.xml import xml_wrap
from ..models import ID_LEN


# =============================================================================
class PubliForgeScaffold(PyramidTemplate):
    """Base class for PubliForge scaffold."""

    # -------------------------------------------------------------------------
    @classmethod
    def _get(cls, label, default=None, validate=None, among=None):
        """Get the value for a variable.

        :param str label:
            Label of the question.
        :param str default: (optional)
            Default value. If ``''``, the value is optional.
        :param function validate: (optional)
            Function to validate the value.
        :param tuple among: (optional)
            Closed list of posssible values.
        :rtype: str
        """
        value = None
        while value is None or (default != '' and value == '') or \
                (validate is not None and not validate(value)) or \
                (among is not None and value not in among):
            what = (among is not None and value is None and ' (? for help)') \
                or (among is not None and ' {0}'.format(among)) or ''
            value = cmdline_input('{0}{1}{2}: '.format(
                label, default and ' [%s]' % default or '', what)) or \
                default or ''
        if version_info < (3, 0):
            value = value.decode(stdin.encoding or 'utf8')
        return value


# =============================================================================
class PubliForgeFrontScaffold(PubliForgeScaffold):
    """Class for PubliForge front scaffold."""

    _template_dir = 'Front'
    summary = 'PubliForge front with one local agent'

    # -------------------------------------------------------------------------
    # pylint: disable = arguments-differ
    def pre(self, command, output_dir, variables):
        """Overrides :meth:`pyramid.scaffolds.PyramidTemplate.pre`, adding
        several variables to the default variables list.

        :type  command: pyramid.scripts.pcreate.PCreateCommand
        :param command:
            Command that invoked the template.
        :param str output_dir:
            Full filesystem path where the created package will be created.
        :param dict variables:
            Dictionary of vars passed to the templates for rendering.
        """
        variables['prefix_low'] = self._get(
            'Instance prefix', variables['project'][0:3].lower()).lower()
        variables['default_language'] = self._get('Default language', 'en')

        variables['admin_login'] = make_id(self._get(
            'Administrator login', 'admin'), 'token', ID_LEN)
        variables['admin_name'] = normalize_spaces(self._get(
            'Administrator name', 'Administrator')).encode('utf8')
        variables['admin_password'] = self._get(
            'Administrator password', token(8).lower())
        variables['admin_email'] = self._get(
            'Administrator email',
            '{0}@publiforge.org'.format(variables['admin_login']),
            validate=email_is_valid)

        variables['user_login'] = make_id(self._get(
            'First user login', variables['package']), 'token', ID_LEN)
        variables['user_name'] = self._get(
            'First user name', variables['user_login'].capitalize())
        variables['user_password'] = self._get(
            'First user password', token(8).lower())
        variables['user_email'] = self._get(
            'First user email', '{0}@{1}'.format(
                variables['user_login'],
                variables['admin_email'].partition('@')[2]),
            validate=email_is_valid)

        variables['storage_name'] = normalize_spaces(self._get(
            'First storage name', 'Data')).encode('utf8')
        variables['storage'] = make_id(
            self._get(
                'First storage ID',
                '{0}_{1}'.format(
                    variables['package'],
                    make_id(variables['storage_name'], 'token'))),
            'standard')
        variables['pfproject_name'] = normalize_spaces(self._get(
            'First project name', 'Project 1')).encode('utf8')

        variables['prefix_up'] = variables['prefix_low'].upper()
        variables['encryption'] = token()
        variables['agent_password'] = token()
        variables['storage_id'] = camel_case(variables['storage'])
        variables['pfproject_id'] = make_id(
            variables['pfproject_name'], 'token', ID_LEN)
        variables['htpassword'] = b64encode(
            sha1(variables['admin_password']).digest())

    # -------------------------------------------------------------------------
    def post(self, command, output_dir, variables):
        """Overrides :meth:`pyramid.scaffolds.PyramidTemplate.post`, to
        print some info after a successful scaffolding rendering.

        :type  command: pyramid.scripts.pcreate.PCreateCommand
        :param command:
            Command that invoked the template.
        :param str output_dir:
            Full filesystem path where the created package will be created.
        :param dict variables:
            Dictionary of vars passed to the templates for rendering.
        """
        # pylint: disable = unused-argument
        message = dedent(
            """
            {line}
            Welcome to your new PubliForge instance!

            Activate your Python virtual environment and type:

            (virtualenv)$ cd {directory}
            (virtualenv)$ pfpopulate development.ini
            (virtualenv)$ pserve development.ini

            Documentation: http://doc.publiforge.org
            {line}
        """.format(line='=' * 79, directory=output_dir))
        self.out(message)


# =============================================================================
class PubliForgeLePrismeScaffold(PubliForgeScaffold):
    """Class for PubliForge processor scaffold."""

    _template_dir = 'LePrisme'
    summary = 'PubliForge processor LePrisme'

    # -------------------------------------------------------------------------
    # pylint: disable = arguments-differ
    def pre(self, command, output_dir, variables):
        """Overrides :meth:`pyramid.scaffolds.PyramidTemplate.pre`, adding
        several variables to the default variables list.

        :type  command: pyramid.scripts.pcreate.PCreateCommand
        :param command:
            Command that invoked the template.
        :param str output_dir:
            Full filesystem path where the created package will be created.
        :param dict variables:
            Dictionary of vars passed to the templates for rendering.
        """
        variables['lang'] = self._get('Default language for texts', 'en')
        variables['i18n_label'] = self._get('Label', variables['project'])
        variables['i18n_description'] = self._get('Description', '')
        variables['ancestors'] = self._get('Space separated ancestors', '')
        variables['template_root'] = self._get('Root for templates', '')
        variables['output'] = self._get(
            'Output', 'Result{0}'.format(
                '2' in variables['project'] and '/{0}'.format(
                    variables['project'].partition('2')[2]) or ''))
        variables['output2pack'] = self._get(
            'Output to pack method', '', among=(
                'result2files', 'result2resources', 'result2templates',
                'output2files', 'output2resources', 'output2templates',
                'smart', ''))

        variables['i18n_label'] = normalize_spaces(
            variables['i18n_label']).encode('utf8')
        if variables['i18n_description']:
            variables['i18n_description'] = u'\n\n    ' \
                u'<description xml:lang="{0}">{1}</description>'.format(
                    variables['lang'],
                    xml_wrap(normalize_spaces(
                        variables['i18n_description']), 2)).encode('utf8')
        variables['description'] = variables['i18n_description'][1:].replace(
            ' xml:lang="{0}"'.format(variables['lang']), '')
        if variables['ancestors']:
            ancestors = [
                '<ancestor>{0}</ancestor>'.format(k)
                for k in variables['ancestors'].split()]
            variables['ancestors'] = \
                '\n\n    <ancestors>\n      {0}\n    </ancestors>'.format(
                    '\n      '.join(ancestors))
        if variables['template_root']:
            variables['template_root'] = \
                '\n\n    <templates root="{0}"/>'.format(
                    variables['template_root'])
        if variables['output2pack']:
            variables['output2pack'] = ' add2pack="{0}"'.format(
                variables['output2pack'])

    # -------------------------------------------------------------------------
    # pylint: disable = arguments-differ
    def post(self, command, output_dir, variables):
        """Overrides :meth:`pyramid.scaffolds.PyramidTemplate.post`, to
        print some info after a successful scaffolding rendering.

        :type  command: pyramid.scripts.pcreate.PCreateCommand
        :param command:
            Command that invoked the template.
        :param str output_dir:
            Full filesystem path where the created package will be created.
        :param dict variables:
            Dictionary of vars passed to the templates for rendering.
        """
        # pylint: disable = unused-argument
        message = dedent(
            """
            {line}
            Welcome to your new PubliForge processor LePrisme!

            Use the "{processor_xml}"
            file to activate it in your PubliForge instance.

            Documentation: http://doc.publiforge.org
            {line}
        """.format(line='=' * 79,
                   processor_xml=join(
                       output_dir,
                       '{0}.pfprc.xml'.format(variables['package']))))
        self.out(message)
