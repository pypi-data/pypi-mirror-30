# -*- coding: utf-8 -*-
"""Class to manage a filter to select items among a collection."""

from collections import OrderedDict

from webhelpers2.html import literal
from sqlalchemy.sql import text

from .i18n import _


OPERATORS = OrderedDict((('AND', _('AND')), ('OR', _('OR'))))
COMPARISONS = OrderedDict((
    ('=', '='), ('!=', u'≠'), ('>', '>'), ('>=', _(u'≥')), ('<', '<'),
    ('<=', _(u'≤'))))


# =============================================================================
class Filter(object):
    """A class to manage filters.

    :type  request: pyramid.request.Request
    :param request:
        Current request.
    :param str filter_id:
        Filter ID.
    :param list inputs:
        A list of inputs like
        ``((key, label, is_static, available_values),...)``.
        ``available_values`` is ``None`` for an input with text values,
        ``True`` for those with boolean values and a list of value/label for
        closed list of values.
    :param list initials: (optional)
        Initial conditions.
    :param str remove: (optional)
        Number of the condition to remove from the previous filter.
    :type  comparisons: :class:`OrderedDict`
    :param comparisons: (optional)
        Customize list of comparaisons.

    A filter is a list of AND-conditions.
    Each AND-condition is a list of OR-conditions.
    An OR-condition is a tuple such as ``(key, comparison, value)``.

    The ``comparison`` is one of the items of ``comparisons`` and can be
    ``'='``, ``'!='``, ``'>'``, ``'>='``, ``'<'`` or ``'<='``.
    The ``value`` can be a boolean, a string or a
    :class:`~pyramid.i18n.TranslationString` instance.

    For instance, the filter:

    ``(id=2 OR id>5) AND active AND group!='Foo'`` is stored as:

    ``[[('id', '=', 2), ('id', '>', 5)], [('active', '=', True)],
    [('group', '!=', 'Foo')]]``
    """

    # -------------------------------------------------------------------------
    def __init__(
            self, request, filter_id, inputs, initials=None, remove=None,
            comparisons=COMPARISONS):
        """Constructor method."""
        # pylint: disable = too-many-arguments
        self.filter_id = filter_id
        self._request = request
        self._inputs = OrderedDict(
            [(k[0], (k[1], k[2], k[3])) for k in inputs])
        self._comparisons = comparisons

        # Retrieve last filter
        if 'filters' not in request.session:
            request.session['filters'] = {}
        self._conditions = request.session['filters'].get(filter_id) or []

        # Append initial conditions
        if filter_id not in request.session['filters'] \
           and initials is not None:
            for condition in initials:
                self.append_condition(*condition)

        # Remove obsolete conditions
        if remove is not None:
            self.remove_condition(remove)

        # Append new conditions
        if 'filter' in request.POST:
            for key in self._inputs:
                if self._inputs[key][1] and \
                   request.POST.get('filter_value_{0}'.format(key)):
                    self.append_condition(
                        key, request.POST.get(
                            'filter_comparison_{0}'.format(key), '='),
                        request.POST['filter_value_{0}'.format(key)],
                        request.POST.get(
                            'filter_operator_{0}'.format(key), 'AND'))
            self.append_condition(
                request.POST.get('filter_key'),
                request.POST.get('filter_comparison', '='),
                request.POST.get('filter_value'),
                request.POST.get('filter_operator', 'AND'))

    # -------------------------------------------------------------------------
    def is_empty(self):
        """Return ``True`` if a filter is empty."""
        return not bool(self._conditions)

    # -------------------------------------------------------------------------
    def clear(self):
        """Clear filter."""
        self._conditions = []
        self._request.session['filters'][self.filter_id] = []

    # -------------------------------------------------------------------------
    def append_condition(self, key, comparison, value, operator='AND'):
        """Append an AND-condition to the filter.

        :param str key:
            The key to use.
        :param str comparison: (``'='``, ``'!='``, ``'>'``, ``'<'``,...)
            How to compare.
        :type  value: :class:`str`, :class:`bool` or
            :class:`~pyramid.i18n.TranslationString`
        :param value:
            The value of the filter. It is optional for boolean filter and its
            default value is ``True``.
        :param str operator: ('AND' or 'OR', default='AND')
            The operator to use to complete the filter.
        """
        if not key or not value or key not in self._inputs or \
           comparison not in self._comparisons or operator not in OPERATORS:
            return
        condition = (
            key, comparison,
            (self._inputs[key][2] is True and True) or value)
        if self._conditions and operator == 'OR':
            self._conditions[-1].append(condition)
        else:
            self._conditions.append([condition])
        self._request.session['filters'][self.filter_id] = self._conditions

    # -------------------------------------------------------------------------
    def remove_condition(self, index):
        """Remove one AND-condition of the filter.

        :param str index:
            Index of the AND-condition to remove.
        """
        if index is None or not index.isdigit():
            return
        index = int(index)
        if index < 0 or index >= len(self._conditions):
            return
        del self._conditions[index]
        self._request.session['filters'][self.filter_id] = self._conditions

    # -------------------------------------------------------------------------
    def html_conditions(self):
        """An HTML representation of the current conditions.

        :rtype: :class:`webhelpers2.html.literal`
        """
        if not self._conditions:
            return ''

        html = u''
        for and_num, and_condition in enumerate(self._conditions):
            if and_num:
                html += u' <strong>{0}</strong> '.format(
                    self._request.localizer.translate(OPERATORS['AND']))
            html += u'<span class="wbFilterCondition">'\
                u'<input type="submit" value="X" name="crm!{0}.x"/>'.format(
                    and_num)
            for or_num, or_condition in enumerate(and_condition):
                if or_num:
                    html += u' <strong>{0}</strong> '.format(
                        self._request.localizer.translate(OPERATORS['OR']))
                condition = self._inputs[or_condition[0]]
                html += u'<span>{0}{1}'.format(
                    condition[2] is True and or_condition[1] == '!=' and
                    self._request.localizer.translate(_('EXCEPT')) + ' ' or '',
                    self._request.localizer.translate(condition[0]))
                if isinstance(condition[2], (list, tuple)):
                    html += u' {0} {1}'.format(
                        self._comparisons[or_condition[1]],
                        self._request.localizer.translate(
                            dict(condition[2]).get(
                                or_condition[2], or_condition[2])))
                elif condition[2] is not True:
                    html += u' {0} {1}'.format(
                        self._comparisons[or_condition[1]], or_condition[2])
                html += '</span>'
            html += '</span> '
        return literal(html)

    # -------------------------------------------------------------------------
    def html_inputs(self, form, tag='span'):
        """An HTML representation of the current inputs.

        :type  form: :class:`.lib.form.Form`
        :param form:
            Current form.
        :param str tag: (Default='div')
            Tag which wraps each input line.
        :rtype: :class:`webhelpers2.html.literal`
        """
        # Static inputs
        html = ''
        has_static = False
        inputs = []
        for key in self._inputs:
            if self._conditions or not self._inputs[key][1]:
                inputs.append((key, self._inputs[key][0]))
                continue
            has_static = True
            html += literal('<{0} class="wbFilterInput">'.format(tag))
            html += literal('<span class="wbFilterNoOp"> </span>')
            html += literal(
                u'<span class="wbFilterKey"><span>{0}</span></span>'.format(
                    self._request.localizer.translate(
                        self._inputs[key][0])))
            html += self._html_select_comparison(form, key)
            html += self._html_select_value(form, key)
            html += literal('</{0}>'.format(tag))
        if not inputs:
            return literal(html)

        # Dynamic inputs
        html += literal('<{0} class="wbFilterInput">'.format(tag))
        key = self._request.POST.get('filter_key') or \
            not has_static and inputs[0][0]
        if self._conditions:
            html += literal('<span class="wbFilterOp">') + \
                form.select('filter_operator', None, OPERATORS.items()) + \
                literal('</span>')
        else:
            html += literal('<span class="wbFilterNoOp"> </span>')
        if has_static:
            inputs.insert(0, ('', u' '))
        html += literal('<span class="wbFilterKey">') + form.select(
            'filter_key', None, inputs, True) + literal('</span>')
        html += self._html_select_comparison(form, key, 'filter_comparison')
        html += self._html_select_value(form, key, 'filter_value')
        html += literal('</{0}>'.format(tag))

        return html

    # -------------------------------------------------------------------------
    def sql(self, dbquery, table_name):
        """Complete a SqlAlchemy query with of the current filter.

        :param sqlalchemy.orm.query.Query dbquery:
            SqlAlchemy query to complete.
        :param str table_name:
            Name of the default SQL table.
        :rtype: sqlalchemy.orm.query.Query
        """
        if not self._conditions:
            return dbquery

        like = 'ILIKE' if dbquery.session.bind.dialect.name == 'postgresql' \
            else 'LIKE'
        for and_num, and_condition in enumerate(self._conditions):
            clause = u'('
            params = {}
            for or_num, or_condition in enumerate(and_condition):
                if or_num:
                    clause += u' OR '
                available_values = self._inputs[or_condition[0]][2]
                if or_condition[1] == '=' and available_values is None:
                    comparison = like
                elif or_condition[1] == '!=' and available_values is None:
                    comparison = 'NOT {0}'.format(like)
                else:
                    comparison = or_condition[1]
                value = True if available_values is True else or_condition[2]
                clause += u'{0}.{1} {2} :p{3}{4:02d}'.format(
                    table_name, or_condition[0], comparison, and_num, or_num)
                params['p{0}{1:02d}'.format(and_num, or_num)] = \
                    u'%{0}%'.format(value) if like in comparison else value
            clause += u')'
            dbquery = dbquery.filter(text(clause).bindparams(**params))

        return dbquery

    # -------------------------------------------------------------------------
    def whoosh(self):
        """Return the current filter in Whoosh query language.

        :rtype: tuple
        :return:
            a tuble search as ``(fieldnames, query)``.
        """
        fieldnames = set()
        clause = u''
        for and_num, and_condition in enumerate(self._conditions):
            if and_num:
                clause += u' AND '
            clause += u'('
            for or_num, or_condition in enumerate(and_condition):
                if or_num:
                    clause += u' OR '
                fieldnames.add(or_condition[0])
                comparison = or_condition[1]
                if or_condition[2] is True:
                    clause += u'{0}{1}:TRUE'.format(
                        comparison == '!=' and 'NOT ' or '', or_condition[0])
                elif comparison == '=':
                    clause += u'{0}:({1})'.format(
                        or_condition[0], or_condition[2])
                elif comparison == '!=':
                    clause += u'NOT {0}:({1})'.format(
                        or_condition[0], or_condition[2])
                elif comparison == '>':
                    clause += u'{0}:{{{1} TO}}'.format(
                        or_condition[0], or_condition[2])
                elif comparison == '>=':
                    clause += u'{0}:[{1} TO]'.format(
                        or_condition[0], or_condition[2])
                elif comparison == '<':
                    clause += u'{0}:{{TO {1}}}'.format(
                        or_condition[0], or_condition[2])
                elif comparison == '<=':
                    clause += u'{0}:[TO {1}]'.format(
                        or_condition[0], or_condition[2])
            clause += u')'

        return tuple(fieldnames), clause

    # -------------------------------------------------------------------------
    def _html_select_comparison(self, form, key, name=None):
        """HTML form select to choose the comparison operator of a condition.

        :type  form: :class:`.lib.form.Form`
        :param form:
            Current form.
        :param str key:
            Current condition key.
        :param str name: (optional)
            Name of the form select.
        :rtype: :class:`webhelpers2.html.literal`
        """
        if name is None:
            name = 'filter_comparison_{0}'.format(key)
        if key and self._inputs[key][2] is not None:
            return literal('<span class="wbFilterComparison">') + \
                form.select(name, None, (('=', '='), ('!=', u'≠'))) + \
                literal('</span>')
        return literal('<span class="wbFilterComparison">') + \
            form.select(name, None, self._comparisons.items()) + \
            literal('</span>')

    # -------------------------------------------------------------------------
    def _html_select_value(self, form, key, name=None):
        """HTML form select to choose the value of a condition.

        :type  form: :class:`.lib.form.Form`
        :param form:
            Current form.
        :param str key:
            Current condition key.
        :param str name: (optional)
            Name of the form select.
        :rtype: :class:`webhelpers2.html.literal`
        """
        if name is None:
            name = 'filter_value_{0}'.format(key)
        if key and self._inputs[key][2] is True:
            return literal('<span class="wbFilterValue">') + \
                form.custom_checkbox(name) + literal('</span>')
        if key and self._inputs[key][2] is not None:
            return literal('<span class="wbFilterValue">') + \
                form.select(name, None, self._inputs[key][2]) + \
                literal('</span>')
        return literal('<span class="wbFilterValue">') + \
            form.text(name, placeholder=self._request.localizer.translate(
                _('type here...'))) + literal('</span>')
