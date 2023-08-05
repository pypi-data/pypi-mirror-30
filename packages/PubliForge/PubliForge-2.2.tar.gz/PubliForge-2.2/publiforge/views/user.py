# pylint: disable = C0322
"""User view callables."""

from datetime import datetime
from colander import Mapping, SchemaNode, String, Integer, Date
from colander import All, Length, OneOf, Email, Regex

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPFound, HTTPNotFound

from ..lib.i18n import _
from ..lib.log import log_activity
from ..lib.config import settings_get_list
from ..lib.utils import has_permission, normalize_name, age
from ..lib.xml import upload_configuration, export_configuration
from ..lib.viewutils import get_action, paging_users
from ..lib.form import SameAs, Form
from ..lib.tabset import TabSet
from ..lib.paging import PAGE_SIZES
from ..models import ID_LEN, LABEL_LEN, DBSession, close_dbsession
from ..models.users import PERM_SCOPES, USER_PERMS, HOMES, PAGE_SIZE
from ..models.users import USER_STATUS, User, UserPerm, UserIP
from ..models.groups import Group


USER_SETTINGS_TABS = (_('Identity'), _('Permissions'), _('Security'))


# =============================================================================
class UserView(object):
    """Class to manage users."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(
        route_name='user_admin', renderer='../Templates/usr_admin.pt',
        permission='usr.update')
    def admin(self):
        """List users for administration purpose."""
        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'usr_manager', 'user')
            log_activity(self._request, 'user_import')
            action = ''
        elif action[0:4] == 'del!':
            self._delete_users(items)
            action = ''
        elif action[0:4] == 'exp!':
            action = self._export_users(items)
            if action:
                return action

        paging, defaults = paging_users(self._request, False)
        form = Form(self._request, defaults=defaults)

        depth = 3 if self._request.breadcrumbs.current_path() == \
            self._request.route_path('site_admin') else 2
        self._request.breadcrumbs.add(_('User administration'), depth)
        return {
            'form': form, 'paging': paging, 'action': action,
            'groups': DBSession.query(Group.group_id, Group.label).all(),
            'USER_STATUS': USER_STATUS, 'PAGE_SIZES': PAGE_SIZES,
            'i_editor': has_permission(self._request, 'usr_editor'),
            'i_manager': has_permission(self._request, 'usr_manager')}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='user_account', renderer='../Templates/usr_view.pt')
    @view_config(route_name='user_view', renderer='../Templates/usr_view.pt')
    def view(self):
        """Show user settings."""
        user_id = self._request.matchdict.get('user_id') \
            or self._request.session['user_id']
        user_id = int(user_id)
        if user_id != self._request.session['user_id'] \
                and not has_permission(self._request, 'usr_editor'):
            raise HTTPForbidden()

        action = get_action(self._request)[0]
        if action == 'exp!':
            action = self._export_users((user_id,))
            if action:
                return action

        user = DBSession.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise HTTPNotFound()
        tab_set = TabSet(self._request, USER_SETTINGS_TABS)
        i_editor = has_permission(self._request, 'usr_editor') \
            or self._request.session['user_id'] == user_id

        self._request.breadcrumbs.add(
            _('User settings'), replace=self._request.route_path(
                'user_edit', user_id=user.user_id))
        return {
            'age': age, 'tab_set': tab_set, 'USER_STATUS': USER_STATUS,
            'HOMES': HOMES, 'PERM_SCOPES': PERM_SCOPES,
            'USER_PERMS': USER_PERMS, 'user': user, 'i_editor': i_editor}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='user_create', renderer='../Templates/usr_edit.pt',
        permission='usr.create')
    def create(self):
        """Create a user."""
        homes = dict([(k, HOMES[k]) for k in HOMES if k != 'site'])
        form, tab_set = self._settings_form()

        if form.validate():
            dbuser = self._create(form.values)
            if dbuser is not None:
                self._request.breadcrumbs.pop()
                log_activity(self._request, 'user_create', dbuser.login)
                return HTTPFound(self._request.route_path(
                    'user_edit', user_id=dbuser.user_id))
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        self._request.breadcrumbs.add(_('User creation'))
        return {
            'form': form, 'tab_set': tab_set,
            'USER_STATUS': USER_STATUS, 'homes': homes,
            'PERM_SCOPES': PERM_SCOPES, 'USER_PERMS': USER_PERMS,
            'languages': settings_get_list(
                self._request.registry.settings, 'languages'),
            'user': None,
            'page_sizes': PAGE_SIZES[1:-1], 'is_me': False,
            'i_admin': False, 'i_manager': True}

    # -------------------------------------------------------------------------
    @view_config(route_name='user_edit', renderer='../Templates/usr_edit.pt')
    def edit(self):
        """Edit user settings."""
        # Authorization
        user_id = int(self._request.matchdict.get('user_id'))
        if user_id != self._request.session['user_id'] \
                and not has_permission(self._request, 'usr_editor'):
            raise HTTPForbidden()
        dbuser = DBSession.query(User).filter_by(user_id=user_id).first()
        if dbuser is None:
            raise HTTPNotFound()

        # Action
        action = get_action(self._request)[0]
        if action[0:4] == 'rmv!':
            DBSession.query(UserIP).filter_by(
                user_id=user_id, ip=action[4:]).delete()
            DBSession.commit()

        # Environment
        homes = dict([(k, HOMES[k]) for k in HOMES if k != 'site'])
        is_me = dbuser.user_id == self._request.session['user_id']
        i_admin = bool([k for k in dbuser.perms if k.level == 'admin'])
        i_manager = has_permission(self._request, 'usr_manager')
        form, tab_set = self._settings_form(dbuser)

        # Save
        update_perms = i_manager and not i_admin and not is_me
        if action == 'sav!' and form.validate(dbuser) \
                and self._save(dbuser, form.values, update_perms):
            if is_me:
                dbuser.setup_environment(self._request)
            log_activity(self._request, 'user_edit', dbuser.login)
            return HTTPFound(self._request.route_path(
                'user_view', user_id=dbuser.user_id))
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('User settings'), replace=self._request.route_path(
                'user_view', user_id=dbuser.user_id))

        return {
            'form': form, 'action': action, 'tab_set': tab_set,
            'USER_STATUS': USER_STATUS, 'homes': homes,
            'PERM_SCOPES': PERM_SCOPES, 'USER_PERMS': USER_PERMS,
            'languages': settings_get_list(
                self._request.registry.settings, 'languages'),
            'user': dbuser,
            'page_sizes': PAGE_SIZES[1:-1], 'is_me': is_me,
            'i_admin': i_admin, 'i_manager': i_manager}

    # -------------------------------------------------------------------------
    def _delete_users(self, user_ids):
        """Delete users.

        :param list user_ids:
            List of user IDs to delete.
        """
        if not has_permission(self._request, 'usr_manager'):
            raise HTTPForbidden()
        user_ids = set([int(k) for k in user_ids])

        # Do not delete myself
        if self._request.session['user_id'] in user_ids:
            self._request.session.flash(
                _("You can't delete your own user."), 'alert')
            return

        # Do not delete administrators
        if DBSession.query(UserPerm).filter(UserPerm.user_id.in_(user_ids))\
                .filter_by(scope='all', level='admin').first() is not None:
            self._request.session.flash(
                _("You can't delete an administrator."), 'alert')
            return

        # Delete
        deleted = []
        for dbuser in DBSession.query(User).filter(User.user_id.in_(user_ids)):
            deleted.append(dbuser.login)
            DBSession.delete(dbuser)
        if deleted:
            DBSession.commit()
            log_activity(self._request, 'user_delete', u' '.join(deleted))

    # -------------------------------------------------------------------------
    def _export_users(self, user_ids):
        """Export users.

        :param list user_ids:
            List of user IDs to export.
        :rtype: :class:`pyramid.response.Response`
        """
        i_manager = has_permission(self._request, 'usr_manager')
        elements = []
        exported = []
        for dbuser in DBSession.query(User)\
                .filter(User.user_id.in_(user_ids)).order_by('login'):
            exported.append(dbuser.login)
            elements.append(dbuser.xml(i_manager))

        elements = [k for k in elements if k is not None]
        if not elements:
            self._request.session.flash(
                _('Nothing to do. (You cannot export administrator)'), 'alert')
            return ''

        name = '%s_users.pfusr' % self._request.registry.settings.get(
            'skin.name', 'publiforge')
        log_activity(
            self._request, 'user_export', u' '.join(exported))

        return export_configuration(elements, name)

    # -------------------------------------------------------------------------
    def _settings_form(self, user=None):
        """Return a user settings form.

        :type  user: :class:`~..models.users.User`
        :param user: (optional)
            Current user object.
        :rtype: tuple
        :return:
            A tuple such as ``(form, tab_set)``.
        """
        # Schema
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='status',
            validator=OneOf(USER_STATUS.keys()), missing='active'))
        schema.add(SchemaNode(
            String(), name='login',
            validator=All(
                Regex(r'^[a-zA-Z_][\w_.-]+$'), Length(max=ID_LEN))))
        if user is None:
            schema.add(SchemaNode(
                String(), name='password1',
                validator=All(
                    Length(min=8), SameAs(self._request, 'password2'))))
            schema.add(SchemaNode(String(), name='password2'))
        else:
            schema.add(SchemaNode(
                String(), name='password1', missing=None,
                validator=All(
                    Length(min=8), SameAs(self._request, 'password2'))))
            schema.add(SchemaNode(String(), name='password2', missing=None))
        schema.add(SchemaNode(
            String(), name='name', validator=Length(max=LABEL_LEN)))
        schema.add(SchemaNode(
            String(), name='email',
            validator=All(Email(), Length(max=LABEL_LEN))))
        schema.add(SchemaNode(
            String(), name='lang',
            validator=OneOf(settings_get_list(
                self._request.registry.settings, 'languages'))))
        schema.add(SchemaNode(
            String(), name='home', validator=OneOf(HOMES.keys())))
        schema.add(SchemaNode(
            Integer(), name='page_size',
            validator=OneOf(PAGE_SIZES[1:-1])))
        schema.add(SchemaNode(Date(), name='expiration', missing=None))
        for scope in PERM_SCOPES:
            schema.add(SchemaNode(
                String(), name='perm_%s' % scope,
                validator=OneOf(USER_PERMS.keys()), missing='-'))
        schema.add(SchemaNode(
            String(), name='new_ip', validator=Regex(r'(\d{1,3}\.){3}\d{1,3}'),
            missing=None))

        # Defaults
        if user is not None:
            defaults = {}
            for perm in user.perms:
                defaults['perm_%s' % perm.scope] = perm.level
        else:
            defaults = {'status': 'active', 'page_size': PAGE_SIZE,
                        'home': 'projects'}

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=user),
            TabSet(self._request, USER_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _create(self, values):
        """Create a user.

        :param values: (dictionary)
            Form values.
        :return: (:class:`~..models.users.User` instance or ``None``)
        """
        # Check existence
        login = normalize_name(values['login'])[0:ID_LEN]
        user = DBSession.query(User).filter_by(login=login).first()
        if user is not None:
            self._request.session.flash(
                _('This user already exists.'), 'alert')
            return None
        if DBSession.query(Group).filter_by(group_id=login)\
                .first() is not None:
            self._request.session.flash(
                _('This identifier already exists.'), 'alert')
            return None

        # Create user
        record = dict([(k, values[k]) for k in values if hasattr(User, k)])
        record['password'] = values['password1']
        if values['new_ip']:
            record['restrict_ip'] = True
        user = User(self._request.registry.settings, **record)
        DBSession.add(user)
        DBSession.commit()

        # Add permissions
        for scope in PERM_SCOPES:
            scope = 'perm_%s' % scope
            if values[scope] != '-':
                user.perms.append(UserPerm(
                    user.user_id, scope[5:], values[scope]))

        # Add IP restriction
        if values['new_ip']:
            user.ips.append(UserIP(user.user_id, values['new_ip']))

        DBSession.commit()
        return user

    # -------------------------------------------------------------------------
    def _save(self, user, values, update_perms):
        """Save a user settings.

        :param user: (:class:`~..models.users.User` instance)
            User to update.
        :param values: (dictionary)
            Form values.
        :param update_perms: (boolean)
            ``True`` if we can update permissions.
        :return: (boolean)
            ``True`` if succeeds.
        """
        # Update user
        if values['password1']:
            user.set_password(
                self._request.registry.settings, values['password1'])

        # Update permissions
        if update_perms:
            perms = dict([(k.scope, k) for k in user.perms])
            for scope in PERM_SCOPES:
                if values['perm_%s' % scope] != '-':
                    if scope in perms:
                        perms[scope].level = values['perm_%s' % scope]
                    else:
                        user.perms.append(UserPerm(
                            user.user_id, scope, values['perm_%s' % scope]))
                elif scope in perms:
                    DBSession.delete(perms[scope])

        # Add IP restriction
        if values['new_ip'] \
                and values['new_ip'] not in [k.ip for k in user.ips]:
            user.ips.append(UserIP(user.user_id, values['new_ip']))

        user.email = user.email.lower() if user.email else None
        user.updated = datetime.now()
        DBSession.commit()
        return True
