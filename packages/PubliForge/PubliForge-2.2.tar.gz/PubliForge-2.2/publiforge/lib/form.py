"""Form validation and rendering library."""

from re import sub

import colander
from webhelpers2.html import tags, HTML, literal

from pyramid.httpexceptions import HTTPNotAcceptable

from .i18n import _


# =============================================================================
class SameAs(object):
    # pylint: disable = too-few-public-methods
    """This class implements a ``colander`` validator to check if to fields are
    identical."""

    # -------------------------------------------------------------------------
    def __init__(self, request, reference):
        """Constructor method."""
        self.request = request
        self.reference = reference

    # -------------------------------------------------------------------------
    def __call__(self, node, value):
        """This method raises a :class:`colander.Invalid` instance as an
        exception value is not same as ``self.reference``.

        :type node: colander.SchemaNode
        :type value: cstruct
        """
        if self.request.POST.get(self.reference) != value:
            raise colander.Invalid(node, _('The two fields are not identical'))


# =============================================================================
def button(url, label='', src=None, title=None, class_='button'):
    """Output a link on a label and an image with a button aspect.

    :param str url:
        Target URL.
    :param str label: (optional)
        Label for roll over and ``alt``.
    :param str src: (optional)
        Image path.
    :param str title: (optional)
        Label for roll over.
    :param str class_: (default='button')
        The class attribute.
    :rtype: str
        HTML tag.
    """
    if class_ == 'button' and not label and src:
        class_ = None
    return literal(u'<a href="{0}"{1}{2}>{3}{4}</a> '.format(
        literal.escape(url), title and ' title="%s"' % title or '',
        class_ and ' class="%s"' % class_ or '',
        src and '<img src="%s" alt="%s"/>' % (src, label or title) or '',
        label))


# =============================================================================
def grid_item(name, label, content, required=False, hint=None, error=None,
              class_=None, tag='div', clear=False):
    """Display an item with label, hint and error message.

    :param str name:
        Input ID.
    :param str label:
        Label.
    :param str content:
        HTML content.
    :param bool required: (default=False)
        Indicate if this field is required.
    :param str hint: (optional)
        Help message.
    :param str error: (optional)
        Error message.
    :param str class_: (optional)
        The class attribute.
    :param str tag: (default='div')
        Tag which contains content, hint and error message.
    :param bool clear: (default=False)
        If ``True``, add a ``<div class="clear"/>`` at the end.
    :rtype: str

    This ouputs a structure such as:

    .. code-block:: html

        <div class="[class_]">
          <label for="[name]"><em>[label]<strong>*</strong></em></label>
          <tag>
            [content]
            <em>[hint]</em>
            <strong class="error">[form.error(name)]</strong>
          </tag>
          <div class="clear"></div>
        </div>

    If ``class_`` is an empty string, ``'formItem'`` is used.
    """
    # pylint: disable = too-many-arguments
    if not content:
        return ''
    if class_ == '':
        class_ = 'formItem'
    class_ = class_ or ''
    if error:
        class_ += ' error'
    return literal(
        u'<div{class_}><label{name}><em>{label}{required}</em></label>'
        u'<{tag}>{content}{hint}{error}</{tag}>{clear}</div>'.format(
            class_=class_ and ' class="%s"' % class_ or '',
            name=name and ' for="%s"' % name or '',
            label=label or '',
            required=HTML.strong('*') if required else '',
            tag=tag,
            content=content,
            hint=HTML.em(' %s' % hint) if hint else '',
            error=HTML.strong(' %s' % error) if error else '',
            clear=clear and '<div class="clear"></div>' or ''))


# =============================================================================
class Form(object):
    """Form validation class."""
    # pylint: disable = too-many-public-methods

    # -------------------------------------------------------------------------
    def __init__(self, request, schema=None, defaults=None, secure=True,
                 obj=None, force_defaults=False):
        """Constructor method."""
        # pylint: disable = too-many-arguments
        self.values = defaults \
            if defaults and (not request.POST or force_defaults) else {}
        self._request = request
        self._schema = schema
        self._secure = secure
        self._errors = {}
        self._special = [[], None]
        self._validated = False
        if obj is not None and schema is not None and not request.POST:
            for field in [k.name for k in schema]:
                if hasattr(obj, field):
                    self.values[field] = getattr(obj, field)

    # -------------------------------------------------------------------------
    def validate(self, obj=None):
        """Check if the form is validated.

        :param object obj: (optional)
            Object to fill.
        :rtype: bool
        :return:
             ``True`` if validated.
        """
        # Something to do?
        if not self._request.POST:
            return False
        if self._validated:
            return not self._errors

        # Cross-site request forgery protection
        if self._secure and self._request.POST.get('_csrf') \
                != self._request.session.get_csrf_token():
            raise HTTPNotAcceptable()

        # Schema validation
        params = dict(self._request.POST.items())
        if self._schema:
            try:
                self.values = self._schema.deserialize(params)
            except colander.Invalid as err:
                self._errors = {}
                for child in err.children:
                    self._errors[child.node.name] = child.messages()
        else:
            self.values.update(params)

        # Fill object
        if obj is not None and not self._errors:
            for field in self.values:
                if hasattr(obj, field):
                    setattr(obj, field, self.values[field])

        self._validated = True
        return len(self._errors) == 0

    # -------------------------------------------------------------------------
    def has_error(self, name=None):
        """Return ``True`` if field ``name`` has an error.

        :param str name: (optional)
            Input ID.
        :rtype: bool
        """
        return bool(name is None and self._errors) or name in self._errors

    # -------------------------------------------------------------------------
    def set_error(self, name, message):
        """Set an error message for field ``name``.

        :param str name:
            Input ID.
        :param str message:
            Error message.
        """
        if name in self._errors:
            self._errors[name].append(message)
        else:
            self._errors[name] = [message]

    # -------------------------------------------------------------------------
    def error(self, name):
        """Return error message for field ``name``.

        :param str name:
            Input ID.
        :rtype: str
        :return:
            Translated error message.
        """
        if name not in self._errors:
            return ''
        return ' ; '.join([self._request.localizer.translate(error)
                           for error in self._errors[name]])

    # -------------------------------------------------------------------------
    def static(self, name):
        """The field ``name`` will not be updated by the form.

        :param str name:
            Name of field to set static.
        """
        if name not in self._special[0]:
            self._special[0].append(name)

    # -------------------------------------------------------------------------
    def forget(self, prefix):
        """Fields beginning by ``prefix`` are forgotten when the page is
        refreshed.

        :param str prefix:
            Prefix to select fields.
        """
        self._special[1] = prefix

    # -------------------------------------------------------------------------
    @classmethod
    def make_safe_id(cls, name):
        """Make a string safe for including in an id attribute

        :param str name:
            String to transform.
        :rtype: str
        """
        return sub(r'(?!-)\W', '', sub(r'\s', '_', name)).lower()

    # -------------------------------------------------------------------------
    def begin(self, url=None, multipart=False, **attrs):
        """Ouput the ``<form>`` tag.

        :param str url: (optional)
            URL to submit form, by default, the current URL.
        :param bool multipart: (default=False)
            If set to ``True``, the enctype is set to ``multipart/form-data``.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        html = tags.form(
            url or self._request.path_qs, 'post', multipart, **attrs)
        if self._secure:
            token = self._request.session.get_csrf_token() \
                or self._request.session.new_csrf_token()
            html += HTML.div(self.hidden('_csrf', token), class_='hidden')
        return html

    # -------------------------------------------------------------------------
    @classmethod
    def end(cls):
        """Ouput the ``</form>`` tag."""
        return tags.end_form()

    # -------------------------------------------------------------------------
    @classmethod
    def submit(cls, name, label=None, class_='button', **attrs):
        """Output a submit button with the label as the caption.

        :param str name:
            Input ID.
        :param str label: (optional)
            Button caption.
        :param str class_: (default='button')
            The class attribute.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        return tags.submit(name, label, class_=class_, **attrs)

    # -------------------------------------------------------------------------
    @classmethod
    def submit_image(cls, name, label, src, class_=None):
        """Output an image submit button.

        :param str name:
            Input ID.
        :param str label:
            Label for roll over and ``alt``.
        :param str src:
            Image path.
        :param str class_:
            The class attribute.
        :rtype: str
        :return:
            HTML tag.
        """
        label = label.replace('"', "'")
        return literal(
            u'<input type="image" name="{0}" src="{1}" title="{2}"'
            ' alt="{2}"{3}/>'.format(
                name, src, label or name,
                class_ and ' class="%s"' % class_ or ''))

    # -------------------------------------------------------------------------
    @classmethod
    def submit_cancel(cls, label):
        """Output a cancel submit button.

        :param str label:
            Label for roll over and ``alt``.
        :rtype: str
        :return:
            HTML tag.
        """
        label = label.replace('"', "'")
        return literal(
            u'<input type="image" name="ccl!" '
            'src="/Static/Images/action_cancel.png" title="{0}" '
            'alt="{0}"/>'.format(label))

    # -------------------------------------------------------------------------
    @classmethod
    def button(cls, url, label='', src=None, title=None, class_='button'):
        """Output a link on a label and an image with a button aspect.

        See :func:`button`.
        """
        return button(url, label, src, title, class_)

    # -------------------------------------------------------------------------
    @classmethod
    def grid_item(cls, label, content, required=False, hint=None,
                  error=None, class_=None, tag='div', clear=False):
        """Output an item with label, hint and error message.

        See :func:`grid_item`.
        """
        # pylint: disable = too-many-arguments
        return grid_item(
            None, label, content, required, hint, error, class_, tag, clear)

    # -------------------------------------------------------------------------
    def hidden(self, name, value=None, **attrs):
        """Output a hidden field.

        :param str name:
            Input ID.
        :param str value: (optional)
            Hidden value.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        return tags.hidden(name, self._value(name, value), **attrs)

    # -------------------------------------------------------------------------
    def text(self, name, value=None, **attrs):
        """Output a standard text field.

        :param str name:
            Input ID.
        :param str value: (optional)
            Default value.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
             HTML tag.
        """
        return tags.text(name, self._value(name, value), **attrs)

    # -------------------------------------------------------------------------
    def password(self, name, value=None, **attrs):
        """Output a password field.

        This method takes the same options as text().
        """
        return tags.password(name, self._value(name, value), **attrs)

    # -------------------------------------------------------------------------
    def checkbox(self, name, value=u'1', checked=False, **attrs):
        """Output a check box.

        :param str name:
            Input ID.
        :param str value: (default=u'1')
            The value to return to the application if the box is checked.
        :param bool checked: (default=False)
            ``True`` if the box should be initially checked.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        return tags.checkbox(
            name, value, checked or self._value(name), **attrs)

    # -------------------------------------------------------------------------
    def custom_checkbox(
            self, name, value=u'1', checked=False, class_=None, **attrs):
        """Output a check box followed by an empty label to customize the
        aspect of the box.

        :param str name:
            Input ID.
        :param str value: (default=u'1')
            The value to return to the application if the box is checked.
        :param bool checked: (default=False)
            ``True`` if the box should be initially checked.
        :param str class_: (default='wbCustomCheckbox')
            The class attribute.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        if class_ is None:
            class_ = 'wbCustomCheckbox'
        return literal('{0}{1}'.format(
            tags.checkbox(
                name, value, checked or self._value(name), class_=class_,
                **attrs),
            '<label for="{0}" class="{1}"> </label>'.format(
                self.make_safe_id(name), class_)))

    # -------------------------------------------------------------------------
    def radio(self, name, value, checked=False, **attrs):
        """Output a radio button.

        :param str name:
            Input ID.
        :param str value: (default='1')
            The value to return to the application if the radio is checked.
        :param bool checked: (default=False)
            ``True`` if the radio should be initially checked.
        :param str label: (optional)
            A text label to display to the right of the radio.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        return tags.radio(
            name, value, checked or value == self._value(name), **attrs)

    # -------------------------------------------------------------------------
    def select(self, name, selected_values, options, autosubmit=False,
               **attrs):
        """Output a dropdown selection box.

        :param str name:
            Input ID.
        :type  selected_value: :class:`str` or :class:`list`
        :param selected_value:
            A string or list of strings or integers giving the value(s) that
            should be preselected.
        :type options:
            (list of :class:`str`, :class:`int` or ``(value, label)`` pairs)
        :param options:
            The label will be shown on the form; the option will be returned to
            the application if that option is chosen. If you pass a ``string``
            or ``int`` instead of a ``2-tuple``, it will be used for both the
            value and the label.
        :param bool autosubmit: (default=False)
            If ``True``, it adds ``onchange="submit()"`` attribute.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        if not options:
            return ''
        opts = []
        translate = self._request.localizer.translate
        for opt in options:
            if isinstance(opt, tuple):
                opts.append(
                    tags.Option(translate(opt[1]), u'{0}'.format(opt[0])))
            else:
                opts.append(tags.Option(u'{0}'.format(opt)))
        return tags.select(
            name, u'{0}'.format(self._value(name, selected_values)),
            tags.Options(opts),
            onchange='submit()' if autosubmit else None, **attrs)

    # -------------------------------------------------------------------------
    def upload(self, name, value=None, **attrs):
        """Output a file upload field.

        :param str name:
            Input ID.
        :param str value: (optional)
            Default value.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        return tags.file(name, self._value(name, value), **attrs)

    # -------------------------------------------------------------------------
    def textarea(self, name, content='', **attrs):
        """Output a text input area.

        :param str name:
            Input ID.
        :param str content: (optional)
            Default value.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            HTML tag.
        """
        return tags.textarea(name, self._value(name, content), **attrs)

    # -------------------------------------------------------------------------
    def grid_text(self, name, label, required=False, hint=None, class_='',
                  clear=False, **attrs):
        """Output a standard text field in a CSS grid layout.

        :param str name:
            Input ID.
        :param str label:
            Label.
        :param bool required: (default=False)
            Indicate if this field is required.
        :param str hint: (optional)
            Help message.
        :param str class_: (optional)
            The class attribute.
        :param bool clear: (default=False)
            If ``True``, add a ``<div class="clear"/>`` at the end.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            Output a grid layout.
        """
        # pylint: disable = too-many-arguments
        return grid_item(
            name, label, self.text(name, **attrs), required, hint,
            self.error(name), class_, clear=clear)

    # -------------------------------------------------------------------------
    def grid_password(self, name, label, required=False, hint=None, class_='',
                      clear=False, **attrs):
        """Output a password field in a CSS grid layout.

        This method takes the same options as grid_text().
        """
        # pylint: disable = too-many-arguments
        return grid_item(
            name, label, self.password(name, **attrs), required, hint,
            self.error(name), class_, clear=clear)

    # -------------------------------------------------------------------------
    def grid_checkbox(self, name, label, required=False, hint=None, class_='',
                      clear=False, **attrs):
        """Output a check box in a CSS grid layout.

        :param str name:
            Input ID.
        :param str label:
            Label.
        :param bool required: (default=False)
            Indicate if this field is required.
        :param str hint: (optional)
            Help message.
        :param str class_: (optional)
            The class attribute.
        :param bool clear: (default=False)
            If ``True``, add a ``<div class="clear"/>`` at the end.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            Output a grid layout.
        """
        # pylint: disable = too-many-arguments
        return grid_item(
            name, label, self.checkbox(name, **attrs), required, hint,
            self.error(name), class_, tag='span', clear=clear)

    # -------------------------------------------------------------------------
    def grid_custom_checkbox(self, name, label, required=False, hint=None,
                             clear=False, class_='formItem', **attrs):
        """Output a custom check box in a CSS grid layout.

        :param str name:
            Input ID.
        :param str label:
            Label.
        :param bool required: (default=False)
            Indicate if this field is required.
        :param str hint: (optional)
            Help message.
        :param bool clear: (default=False)
            If ``True``, add a ``<div class="wbClear"/>`` at the end.
        :param str class_: (optional)
            The class attribute.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            Output a grid layout.
        """
        # pylint: disable = too-many-arguments
        return grid_item(
            name, label, self.custom_checkbox(name, **attrs), required, hint,
            self.error(name), class_, tag='span', clear=clear)

    # -------------------------------------------------------------------------
    def grid_select(self, name, label, options, autosubmit=False,
                    required=False, hint=None, class_='', clear=False,
                    **attrs):
        """Output a dropdown selection box in a CSS grid layout.

        :param str name:
            Input ID.
        :param str label:
            Label.
        :type options:
            (list of :class:`str`, :class:`int` or ``(value, label)`` pairs)
        :param options:
            Values in the dropdown list.
        :param bool autosubmit: (default=False)
            If ``True``, it adds ``onchange="submit()"`` attribute.
        :param bool required: (default=False)
            Indicate if this field is required.
        :param str hint: (optional)
            Help message.
        :param str class_: (optional)
            The class attribute.
        :param bool clear: (default=False)
            If ``True``, add a ``<div class="clear"/>`` at the end.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            Output a grid layout.
        """
        # pylint: disable = too-many-arguments
        return grid_item(
            name, label, self.select(name, None, options, autosubmit, **attrs),
            required, hint, self.error(name), class_, clear=clear)

    # -------------------------------------------------------------------------
    def grid_upload(self, name, label, required=False, hint=None, class_='',
                    clear=False, **attrs):
        """Output a file upload field in a CSS grid layout.

        :param str name:
            Input ID.
        :param str label:
            Label.
        :param bool required: (default=False)
            Indicate if this field is required.
        :param str hint: (optional)
            Help message.
        :param str class_: (optional)
            The class attribute.
        :param bool clear: (default=False)
            If ``True``, add a ``<div class="clear"/>`` at the end.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            Output a grid layout.
        """
        # pylint: disable = too-many-arguments
        return grid_item(
            name, label, self.upload(name, **attrs), required, hint,
            self.error(name), class_, clear=clear)

    # -------------------------------------------------------------------------
    def grid_textarea(self, name, label, required=False, hint=None, class_='',
                      clear=False, **attrs):
        """Output a text input area in a CSS grid layout.

        :param str name:
            Input ID.
        :param str label:
            Label.
        :param bool required: (default=False)
            Indicate if this field is required.
        :param str hint: (optional)
            Help message.
        :param str class_: (optional)
            The class attribute.
        :param bool clear: (default=False)
            If ``True``, add a ``<div class="clear"/>`` at the end.
        :param dict attrs:
            Keyworded arguments for ``webhelpers2.html.tags`` object.
        :rtype: str
        :return:
            Output a grid layout.
        """
        # pylint: disable = too-many-arguments
        return grid_item(
            name, label, self.textarea(name, **attrs), required, hint,
            self.error(name), class_, clear=clear)

    # -------------------------------------------------------------------------
    def _value(self, name, default=None):
        """Return the best value for the field ``name``.

        :param str name:
            Input ID.
        :param str default: (optional)
            Default value.
        :rtype: str
        """
        if name not in self._special[0] and \
           (not self._special[1] or not name.startswith(self._special[1])) and\
           name in self._request.POST:
            return self._request.POST[name]
        elif name in self.values:
            return self.values[name]
        return default
