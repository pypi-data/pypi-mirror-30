# pylint: disable = C0322
"""Indexer view callables."""

from cPickle import loads, dumps
from colander import Mapping, SchemaNode, String, Integer
from colander import All, Length, Regex, OneOf
from sqlalchemy import desc

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden

from ..lib.i18n import _
from ..lib.log import log_activity
from ..lib.config import settings_get_list
from ..lib.utils import has_permission, make_id, normalize_spaces
from ..lib.xml import upload_configuration, export_configuration
from ..lib.viewutils import get_action
from ..lib.form import Form
from ..lib.tabset import TabSet
from ..lib.paging import PAGE_SIZES, Paging
from ..models import ID_LEN, VALUE_LEN, PATTERN_LEN, DBSession, close_dbsession
from ..models.indexers import INDEX_VALUE_TYPES, DISPLAYS, EXTRACTOR_TYPES
from ..models.indexers import Indexer, IndexerExtractor, IndexerValue


INDEXER_SETTINGS_TABS = (
    _('Description'), _('Extractors'), _('Closed list of values'))


# =============================================================================
class IndexerView(object):
    """Class to manage indexers."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(
        route_name='indexer_admin', renderer='../Templates/idx_admin.pt',
        permission='idx.update')
    def admin(self):
        """List indexers for administration purpose."""
        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'idx_manager', 'indexer')
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()
            log_activity(self._request, 'indexer_import')
            action = ''
        elif action[0:4] == 'del!':
            self._delete_indexers(items)
            action = ''
        elif action[0:4] == 'exp!':
            action = self._export_indexers(items)
            if action:
                return action

        paging, defaults = self._paging_indexers()
        lang = self._request.session['lang']
        default_lang = self._request.registry.settings.get(
            'pyramid.default_locale_name', 'en')
        labels = dict([
            (k.indexer_id, k.label(lang, default_lang)) for k in paging])
        form = Form(self._request, defaults=defaults)

        depth = 3 if self._request.breadcrumbs.current_path() == \
            self._request.route_path('site_admin') else 2
        self._request.breadcrumbs.add(_('Indexing administration'), depth)
        return {
            'form': form, 'paging': paging, 'action': action, 'labels': labels,
            'i_editor': has_permission(self._request, 'idx_editor'),
            'i_manager': has_permission(self._request, 'idx_manager'),
            'INDEX_VALUE_TYPES': INDEX_VALUE_TYPES, 'PAGE_SIZES': PAGE_SIZES}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='indexer_view', renderer='../Templates/idx_view.pt',
        permission='idx.read')
    def view(self):
        """Show indexer settings."""
        indexer_id = self._request.matchdict.get('indexer_id')
        action = get_action(self._request)[0]
        if action == 'exp!':
            return self._export_indexers((indexer_id,))

        indexer = DBSession.query(Indexer).filter_by(
            indexer_id=indexer_id).first()
        if indexer is None:
            raise HTTPNotFound()
        labels = loads(str(indexer.labels))
        label = indexer.label(
            self._request.session['lang'],
            self._request.registry.settings.get(
                'pyramid.default_locale_name', 'en'))
        tab_set = TabSet(self._request, INDEXER_SETTINGS_TABS)

        self._request.breadcrumbs.add(
            _('Indexer settings'), replace=self._request.route_path(
                'indexer_edit', indexer_id=indexer.indexer_id))
        return {
            'tab_set': tab_set, 'indexer': indexer, 'labels': labels,
            'label': label, 'INDEX_VALUE_TYPES': INDEX_VALUE_TYPES,
            'EXTRACTOR_TYPES': EXTRACTOR_TYPES,
            'i_editor': has_permission(self._request, 'idx_editor')}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='indexer_create', renderer='../Templates/idx_edit.pt',
        permission='idx.create')
    def create(self):
        """Create an indexer."""
        default_lang = self._request.registry.settings.get(
            'pyramid.default_locale_name', 'en')
        labels = {default_lang: None}
        if self._request.session['lang'] != default_lang:
            labels[self._request.session['lang']] = None
        form, tab_set = self._settings_form(default_lang, labels)

        if form.validate():
            dbindexer = self._create(labels, form.values)
            if dbindexer is not None:
                if 'search' in self._request.session:
                    del self._request.session['search']
                self._request.registry['handler'].delete_index()
                self._request.breadcrumbs.pop()
                log_activity(
                    self._request, 'indexer_create', dbindexer.indexer_id)
                return HTTPFound(self._request.route_path(
                    'indexer_edit', indexer_id=dbindexer.indexer_id))
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        self._request.breadcrumbs.add(_('Indexer creation'))
        return {
            'form': form, 'tab_set': tab_set, 'indexer': None,
            'labels': labels, 'default_lang': default_lang,
            'INDEX_VALUE_TYPES': INDEX_VALUE_TYPES, 'DISPLAYS': DISPLAYS}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='indexer_edit', renderer='../Templates/idx_edit.pt',
        permission='idx.update')
    def edit(self):
        """Edit indexer settings."""
        # Action
        indexer_id = self._request.matchdict.get('indexer_id')
        action = get_action(self._request)[0]
        if action[0:4] == 'del!':
            DBSession.query(IndexerExtractor).filter_by(
                indexer_id=indexer_id, extractor_id=int(action[4:]))\
                .delete()
            DBSession.commit()
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()
        elif action[0:4] == 'dvl!':
            DBSession.query(IndexerValue).filter_by(
                indexer_id=indexer_id, value_id=int(action[4:])).delete()
            DBSession.commit()
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()

        # Environment
        dbindexer = DBSession.query(Indexer).filter_by(
            indexer_id=indexer_id).first()
        if dbindexer is None:
            raise HTTPNotFound()
        default_lang = self._request.registry.settings.get(
            'pyramid.default_locale_name', 'en')
        labels = loads(str(dbindexer.labels))
        for lang in settings_get_list(
                self._request.registry.settings, 'languages'):
            if lang not in labels:
                labels[lang] = None
        label = dbindexer.label(self._request.session['lang'], default_lang)
        form, tab_set = self._settings_form(default_lang, labels, dbindexer)

        # Save
        view_path = self._request.route_path(
            'indexer_view', indexer_id=dbindexer.indexer_id)
        if action == 'sav!' and form.validate(dbindexer) \
                and self._save(labels, dbindexer, form.values):
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()
            log_activity(
                self._request, 'indexer_edit', dbindexer.indexer_id)
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(_('Indexer settings'), replace=view_path)

        return {
            'form': form, 'action': action, 'tab_set': tab_set,
            'indexer': dbindexer, 'labels': labels, 'label': label,
            'default_lang': default_lang,
            'INDEX_VALUE_TYPES': INDEX_VALUE_TYPES, 'DISPLAYS': DISPLAYS,
            'EXTRACTOR_TYPES': EXTRACTOR_TYPES}

    # -------------------------------------------------------------------------
    def _paging_indexers(self):
        """Return a :class:`~.widget.Paging` object filled with indexers.

        :return: (tuple)
            A tuple such as ``(paging, filters)`` where ``paging`` is a
            :class:`~.widget.Paging` object and ``filters`` a dictionary of
            filters.
        """
        # Parameters
        params = Paging.params(self._request, 'indexers', '+indexer_id')

        # Query
        query = DBSession.query(Indexer)
        if 'f_id' in params:
            query = query.filter(
                Indexer.indexer_id.like('%%%s%%' % params['f_id'].lower()))

        # Order by
        oby = getattr(Indexer, params['sort'][1:])
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, 'indexers', query), params

    # -------------------------------------------------------------------------
    def _delete_indexers(self, indexer_ids):
        """Delete indexers.

        :param list user_ids:
            List of indexers to delete.
        """
        if not has_permission(self._request, 'idx_manager'):
            raise HTTPForbidden()

        # Delete
        deleted = []
        for dbindexer in DBSession.query(Indexer).filter(
                Indexer.indexer_id.in_(indexer_ids)):
            deleted.append(dbindexer.indexer_id)
            DBSession.delete(dbindexer)
        if not deleted:
            return

        DBSession.commit()
        if 'search' in self._request.session:
            del self._request.session['search']
        self._request.registry['handler'].delete_index()
        log_activity(self._request, 'indexer_delete', u' '.join(deleted))

    # -------------------------------------------------------------------------
    def _export_indexers(self, indexer_ids):
        """Export indexers.

        :param list user_ids:
            List of user IDs to export.
        :rtype: :class:`pyramid.response.Response`
        """
        elements = []
        exported = []
        for dbindexer in DBSession.query(Indexer)\
                .filter(Indexer.indexer_id.in_(indexer_ids))\
                .order_by('indexer_id'):
            exported.append(dbindexer.indexer_id)
            elements.append(dbindexer.xml())

        name = '%s_indexers.pfidx' % self._request.registry.settings.get(
            'skin.name', 'publiforge')
        log_activity(
            self._request, 'indexer_export', u' '.join(exported))

        return export_configuration(elements, name)

    # -------------------------------------------------------------------------
    def _settings_form(self, default_lang, labels, indexer=None):
        """Return a indexer settings form.

        :param str default_lang:
            Default language.
        :param dict labels:
            Label in several languages.
        :type  indexer: :class:`~..models.indexers.Indexer`
        :param indexer: (optional)
            Current indexer object.
        :rtype: tuple
        :return:
            A tuple such as ``(form, tab_set)``.
        """
        # Schema
        defaults = {}
        schema = SchemaNode(Mapping())
        if indexer is None:
            schema.add(SchemaNode(
                String(), name='indexer_id', validator=All(
                    Regex(r'^[a-z_][a-z0-9-_]+$'), Length(max=ID_LEN))))
        for lang in labels:
            if lang == default_lang:
                schema.add(SchemaNode(String(), name='label_%s' % lang))
            else:
                schema.add(SchemaNode(
                    String(), name='label_%s' % lang, missing=None))
            if labels[lang]:
                defaults['label_%s' % lang] = labels[lang].decode('utf8')
        schema.add(SchemaNode(
            String(), name='value_type',
            validator=OneOf(INDEX_VALUE_TYPES.keys())))
        schema.add(SchemaNode(
            String(), name='display', validator=OneOf(DISPLAYS.keys()),
            missing=None))
        schema.add(SchemaNode(Integer(), name='result_column', missing=None))

        # Extractors
        if indexer is not None:
            for extractor in indexer.extractors:
                schema.add(SchemaNode(
                    String(), name='ex_%d_files' % extractor.extractor_id,
                    validator=Length(max=PATTERN_LEN)))
                schema.add(SchemaNode(
                    String(), name='ex_%d_type' % extractor.extractor_id,
                    validator=OneOf(EXTRACTOR_TYPES.keys())))
                schema.add(SchemaNode(
                    String(), name='ex_%d_param' % extractor.extractor_id,
                    validator=Length(max=VALUE_LEN)))
                schema.add(SchemaNode(
                    Integer(), name='ex_%d_limit' % extractor.extractor_id,
                    missing=None))
                defaults['ex_%d_files' % extractor.extractor_id] = \
                    extractor.indexed_files
                defaults['ex_%d_type' % extractor.extractor_id] = \
                    extractor.extractor_type
                defaults['ex_%d_param' % extractor.extractor_id] = \
                    extractor.parameter
                defaults['ex_%d_limit' % extractor.extractor_id] = \
                    extractor.limit
        if self._request.params.get('ex_type'):
            schema.add(SchemaNode(
                String(), name='ex_files',
                validator=Length(max=PATTERN_LEN)))
            schema.add(SchemaNode(
                String(), name='ex_type',
                validator=OneOf(EXTRACTOR_TYPES.keys())))
            schema.add(SchemaNode(
                String(), name='ex_param',
                validator=Length(max=VALUE_LEN)))
            schema.add(SchemaNode(
                Integer(), name='ex_limit', missing=None))

        # Values
        if indexer is not None and \
           indexer.value_type in ('select', 'filetype'):
            for value in indexer.values:
                schema.add(SchemaNode(
                    String(), name='val_%d_label' % value.value_id,
                    validator=Length(max=VALUE_LEN)))
                schema.add(SchemaNode(
                    String(), name='val_%d_value' % value.value_id,
                    validator=Length(max=VALUE_LEN), missing=None))
                defaults['val_%d_label' % value.value_id] = value.label
                defaults['val_%d_value' % value.value_id] = value.value
            if self._request.params.get('val_label'):
                schema.add(SchemaNode(
                    String(), name='val_label',
                    validator=Length(max=VALUE_LEN)))
                schema.add(SchemaNode(
                    String(), name='val_value',
                    validator=Length(max=VALUE_LEN), missing=None))

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=indexer),
            TabSet(self._request, INDEXER_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _create(self, labels, values):
        """Create an indexer.

        :param labels: (dictionary)
            Label in several languages.
        :param values: (dictionary)
            Form values.
        :return: (:class:`~..models.indexers.Indexer` instance or ``None``)
        """
        # Check existence
        indexer_id = make_id(values['indexer_id'], 'token', ID_LEN)
        indexer = DBSession.query(Indexer).filter_by(
            indexer_id=indexer_id).first()
        if indexer is not None:
            self._request.session.flash(
                _('This indexer already exists.'), 'alert')
            return None

        # Create indexer
        indexer = Indexer(
            indexer_id, self._label_dict(labels, values), values['value_type'],
            values['display'], values['result_column'])
        DBSession.add(indexer)
        DBSession.commit()

        return indexer

    # -------------------------------------------------------------------------
    def _save(self, labels, indexer, values):
        """Save an indexer.

        :param labels: (dictionary)
            Label in several languages.
        :param indexer: (:class:`~..models.indexers.Indexer` instance)
            Indexer to save.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
        """
        indexer.labels = dumps(self._label_dict(labels, values))
        if values['value_type'] in ('filename', 'path'):
            DBSession.commit()
            return True

        # Extractors
        for extractor in indexer.extractors:
            extractor.indexed_files = \
                values['ex_%d_files' % extractor.extractor_id]
            extractor.extractor_type = \
                values['ex_%d_type' % extractor.extractor_id]
            extractor.parameter = \
                values['ex_%d_param' % extractor.extractor_id]
            extractor.limit = \
                values['ex_%d_limit' % extractor.extractor_id]
        if values.get('ex_type'):
            indexer.extractors.append(IndexerExtractor(
                values['ex_files'], values['ex_type'], values['ex_param'],
                values['ex_limit']))

        # Values
        for value in indexer.values:
            value.label = \
                normalize_spaces(values['val_%d_label' % value.value_id])
            value.value = normalize_spaces(
                values['val_%d_value' % value.value_id]) \
                if values['val_%d_value' % value.value_id] else value.label
            value.value = value.value if value.value else value.label
        if values.get('val_label'):
            indexer.values.append(IndexerValue(
                values['val_label'], values['val_value']))

        DBSession.commit()
        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _label_dict(cls, langs, values):
        """Return a label dictionary with language as key.

        :param langs: (list)
            Languages to select.
        :param values: (dictionary)
            Form values.
        :return: (dictionay)
        """
        labels = {}
        for lang in langs:
            if values.get('label_%s' % lang):
                labels[lang] = values['label_%s' % lang].encode('utf8')
        return labels
