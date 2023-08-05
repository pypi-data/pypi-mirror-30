# -*- coding: utf-8 -*-
"""Tests of ``lib.form`` functions and class methods."""

from unittest import TestCase

from pyramid.testing import DummyRequest


# =============================================================================
class ULibFormSameAs(TestCase):
    """Unit test class for :class:`lib.form.SameAs`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.form.SameAs]"""
        from colander import Invalid
        from ..lib.form import SameAs

        same_as = SameAs(DummyRequest(), 'foo')
        self.assertRaises(Invalid, same_as, 'login', 'bar')


# =============================================================================
class ULibFormButton(TestCase):
    """Unit test class for :func:`lib.form.button`."""

    # -------------------------------------------------------------------------
    def test_with_no_label(self):
        """[u:lib.form.button] with no label"""
        from ..lib.form import button
        from webhelpers2.html import literal

        test_button = button(url='url', src='src')
        expected_result = \
            literal(u'<a href="url"><img src="src" alt="None"/></a> ')
        self.assertEqual(test_button, expected_result)

    # -------------------------------------------------------------------------
    def test_regular_button(self):
        """[u:lib.form.button] regular button"""
        from ..lib.form import button
        from webhelpers2.html import literal

        test_button = button(
            url='url', label='label', src='src', title='title', class_='value')
        expected_result = \
            literal(u'<a href="url" title="title" class="value">'
                    '<img src="src" alt="label"/>label</a> ')
        self.assertEqual(test_button, expected_result)


# =============================================================================
class ULibFormGridItem(TestCase):
    """Unit test class for :func:`lib.form.grid_item`."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.form.grid_item]"""
        from ..lib.form import grid_item

        self.assertFalse(grid_item(None, 'label', None))
        self.assertEqual(
            grid_item(
                None, 'label', 'html', True, 'help', 'erreur',
                '', 'lt', True),
            u'<div class="formItem error"><label><em>label<strong>*</strong>'
            '</em></label><lt>html<em> help</em><strong> erreur'
            '</strong></lt><div class="clear"></div></div>')
        self.assertEqual(
            grid_item(
                None, 'label', 'html', False, 'help', 'erreur',
                'noClass', 'lt', False),
            u'<div class="noClass error"><label><em>label</em></label><lt>'
            'html<em> help</em><strong> erreur</strong>'
            '</lt></div>')


# =============================================================================
class ULibFormForm(TestCase):
    """Unit test class for :class:`lib.form.Form`."""
    # pylint: disable = too-many-public-methods

    # -------------------------------------------------------------------------
    @classmethod
    def schema(cls):
        """Return a simple Colander schema."""
        from colander import Mapping, SchemaNode, String, Boolean, Length

        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='login', validator=Length(min=2)))
        schema.add(SchemaNode(Boolean(), name='remember', missing=False))
        return schema

    # -------------------------------------------------------------------------
    def test_init(self):
        """[u:lib.form.Form.__init__]"""
        from collections import namedtuple
        from ..lib.form import Form

        request = DummyRequest()
        form = Form(request)
        self.assertFalse(form.values)

        form = Form(request, self.schema())
        self.assertFalse(form.values)

        form = Form(request, self.schema(), defaults={'login': 'user1'})
        self.assertIn('login', form.values)
        self.assertEqual(form.values['login'], 'user1')

        user = namedtuple('User', 'login')(login='user1')
        form = Form(request, self.schema(), obj=user)
        self.assertIn('login', form.values)
        self.assertEqual(form.values['login'], 'user1')

    # -------------------------------------------------------------------------
    def test_validate_request_no_post(self):
        """[u:lib.form.Form.validate] request with no post"""
        from ..lib.form import Form

        form = Form(DummyRequest())
        self.assertFalse(form.validate())

    # -------------------------------------------------------------------------
    def test_validate_csrf(self):
        """[u:lib.form.Form.validate] Cross-site request forgery protection"""
        from pyramid.httpexceptions import HTTPNotAcceptable
        from ..lib.form import Form

        form = Form(DummyRequest(POST={'_crsf': '23SDn4'}))
        self.assertRaises(HTTPNotAcceptable, form.validate)

    # -------------------------------------------------------------------------
    def test_validate_ko(self):
        """[u:lib.form.Form.validate] KO"""
        from colander import Mapping, SchemaNode, String, Boolean, Length
        from ..lib.form import Form

        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='login', validator=Length(min=2)))
        schema.add(SchemaNode(Boolean(), name='remember'))

        form = Form(
            DummyRequest(POST={'login': 'user1'}),
            schema=schema, secure=False)
        self.assertFalse(form.validate())

        form = Form(
            DummyRequest(POST={'login': 'u', 'remember': False}),
            schema=schema, secure=False)
        self.assertFalse(form.validate())

    # -------------------------------------------------------------------------
    def test_validate_ok(self):
        """[u:lib.form.Form.validate] OK"""
        from ..lib.form import Form

        form = Form(
            DummyRequest(POST={'login': 'user1'}), secure=False)
        form.validate()
        self.assertTrue(form.validate())
        self.assertNotIn('remember', form.values)
        self.assertIn('login', form.values)
        self.assertEqual(form.values['login'], 'user1')

        form = Form(
            DummyRequest(POST={'login': 'user1'}),
            schema=self.schema(), secure=False)
        self.assertTrue(form.validate())
        self.assertIn('remember', form.values)
        self.assertFalse(form.values['remember'])
        self.assertIn('login', form.values)
        self.assertEqual(form.values['login'], 'user1')

        class User(object):
            """Dummy user class."""
            # pylint: disable = too-few-public-methods
            login = None
            remember = False

        form = Form(
            DummyRequest(POST={'login': 'user1', 'remember': True}),
            schema=self.schema(), secure=False)
        user = User()
        self.assertTrue(form.validate(user))
        self.assertIn('remember', form.values)
        self.assertTrue(form.values['remember'])
        self.assertEqual(user.login, 'user1')
        self.assertTrue(user.remember)

    # -------------------------------------------------------------------------
    def test_has_error(self):
        """[u:lib.form.Form.has_error]"""
        from ..lib.form import Form

        form = Form(
            DummyRequest(POST={'remember': True}),
            schema=self.schema(), secure=False)
        form.validate()
        self.assertTrue(form.has_error())
        self.assertTrue(form.has_error('login'))
        self.assertFalse(form.has_error('remember'))

    # -------------------------------------------------------------------------
    def test_set_error(self):
        """[u:lib.form.Form.set_error]"""
        from ..lib.form import Form

        form = Form(DummyRequest())
        form.set_error('login', 'required')
        self.assertTrue(form.has_error('login'))

        form = Form(
            DummyRequest(POST={'remember': True}),
            schema=self.schema(), secure=False)
        form.validate()
        form.set_error('login', 'required login')
        self.assertTrue(form.has_error('login'))

    # -------------------------------------------------------------------------
    def test_error(self):
        """[u:lib.form.Form.error]"""
        from ..lib.form import Form

        form = Form(
            DummyRequest(POST={'remember': True}),
            schema=self.schema(), secure=False)
        form.validate()
        self.assertEqual(form.error('login'), 'Required')
        self.assertFalse(form.error('remember'))

    # -------------------------------------------------------------------------
    def test_static(self):
        """[u:lib.form.Form.static]"""
        from ..lib.form import Form

        form = Form(
            DummyRequest(POST={'login': 'user2'}),
            schema=self.schema(), defaults={'login': 'user1'}, secure=False)
        form.static('login')
        input_text = str(form.text('login', 'user1'))
        self.assertIn('user1', input_text)
        self.assertNotIn('user2', input_text)

    # -------------------------------------------------------------------------
    def test_forget(self):
        """[u:lib.form.Form.forget]"""
        from ..lib.form import Form

        form = Form(
            DummyRequest(POST={'login': 'user1'}),
            schema=self.schema(), secure=False)
        form.forget('l')
        input_text = str(form.text('login'))
        self.assertNotIn('user1', input_text)

    # -------------------------------------------------------------------------
    def test_make_safe_id(self):
        """[u:lib.form.Form.make_safe_id]"""
        from ..lib.form import Form

        self.assertEqual(Form.make_safe_id('~Publidoc'), 'publidoc')
        self.assertEqual(Form.make_safe_id('#12'), '12')

    # -------------------------------------------------------------------------
    def test_begin(self):
        """[u:lib.form.Form.begin]"""
        from ..lib.form import Form

        form = Form(DummyRequest(), secure=False)
        html = str(form.begin(url='/login'))
        self.assertEqual(html, '<form action="/login" method="post">')

        html = str(form.begin(url='/login', multipart=True))
        self.assertEqual(
            html,
            '<form action="/login" enctype="multipart/form-data"'
            ' method="post">')

        request = DummyRequest()
        form = Form(request, secure=True)
        html = str(form.begin(url='/login'))
        self.assertEqual(
            html,
            '<form action="/login" method="post"><div class="hidden">'
            '<input id="_csrf" name="_csrf" type="hidden" value="{0}" />'
            '</div>'.format(request.session.new_csrf_token()))

    # -------------------------------------------------------------------------
    def test_end(self):
        """[u:lib.form.Form.end]"""
        from ..lib.form import Form

        html = str(Form(DummyRequest()).end())
        self.assertEqual(html, '</form>')

    # -------------------------------------------------------------------------
    def test_submit(self):
        """[u:lib.form.Form.submit]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).submit('foo', 'Foo')
        self.assertIn('id="foo"', html)
        self.assertIn('value="Foo"', html)
        self.assertIn('class="button"', html)

        html = Form(DummyRequest()).submit('foo', class_='mainButton')
        self.assertIn('class="mainButton"', html)

    # -------------------------------------------------------------------------
    def test_submit_image(self):
        """[u:lib.form.Form.submit_image]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).submit_image('foo', '', 'Images/foo.png')
        self.assertIn('type="image"', html)
        self.assertIn('name="foo"', html)
        self.assertIn('title="foo"', html)

        html = Form(DummyRequest()).submit_image(
            'foo', 'My "Foo"', 'Images/foo.png')
        self.assertIn('title="My \'Foo\'"', html)

        html = Form(DummyRequest()).submit_image(
            'foo', u'éÔ', 'Images/foo.png')
        self.assertIn(u'title="éÔ"', html)

    # -------------------------------------------------------------------------
    def test_submit_cancel(self):
        """[u:lib.form.Form.submit_cancel]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).submit_cancel('Cancel')
        self.assertIn('type="image"', html)
        self.assertIn('name="ccl!"', html)
        self.assertIn('title="Cancel"', html)

    # -------------------------------------------------------------------------
    def test_button(self):
        """[u:lib.form.Form.button]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).button(
            'http://localhost/foo', 'My Foo')
        self.assertIn('href="http://localhost/foo"', html)
        self.assertIn('class="button"', html)

    # -------------------------------------------------------------------------
    def test_grid_item(self):
        """[u:lib.form.Form.grid_item]"""
        from webhelpers2.html import literal
        from ..lib.form import Form

        html = Form(DummyRequest()).grid_item(
            'My label', literal('<input type="test" id="foo">'),
            required=True, hint=u'éÔ', error=u'ôÉ')
        self.assertIn(u'<em> éÔ</em>', html)
        self.assertIn(u'<strong> ôÉ</strong>', html)
        self.assertIn(u'<strong>*</strong>', html)

    # -------------------------------------------------------------------------
    def test_hidden(self):
        """[u:lib.form.Form.hidden]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).hidden('foo', u'éÔ')
        self.assertIn('type="hidden"', html)
        self.assertIn('id="foo"', html)
        self.assertIn(u'value="éÔ"', html)

    # -------------------------------------------------------------------------
    def test_text(self):
        """[u:lib.form.Form.text]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).text('foo', u'éÔ')
        self.assertIn('type="text"', html)
        self.assertIn('id="foo"', html)
        self.assertIn(u'value="éÔ"', html)

    # -------------------------------------------------------------------------
    def test_password(self):
        """[u:lib.form.Form.password]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).password('password', u'seekrit')
        self.assertIn('type="password"', html)
        self.assertIn('id="password"', html)
        self.assertIn(u'value="seekrit"', html)

    # -------------------------------------------------------------------------
    def test_checkbox(self):
        """[u:lib.form.Form.checkbox]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).checkbox('foo', u'éÔ', checked=True)
        self.assertIn('type="checkbox"', html)
        self.assertIn(u'value="éÔ"', html)
        self.assertIn(u'checked="checked"', html)

    # -------------------------------------------------------------------------
    def test_custom_checkbox(self):
        """[u:lib.form.Form.custom_checkbox]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).custom_checkbox('foo')
        self.assertIn('wbCustomCheckbox', html)
        self.assertIn('label', html)
        self.assertIn('type="checkbox"', html)
        self.assertIn(u'value="1"', html)
        self.assertNotIn('checked="checked"', html)

        html = Form(DummyRequest()).custom_checkbox('foo', checked=True)
        self.assertIn('checked="checked"', html)

        html = Form(DummyRequest(POST={'foo': u'1'})).custom_checkbox('foo')
        self.assertIn('checked="checked"', html)

    # -------------------------------------------------------------------------
    def test_radio(self):
        """[u:lib.form.Form.radio]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).radio('foo', u'éÔ', checked=True)
        self.assertIn('type="radio"', html)
        self.assertIn(u'value="éÔ"', html)
        self.assertIn(u'checked="checked"', html)

    # -------------------------------------------------------------------------
    def test_select(self):
        """[u:lib.form.Form.select]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).select(
            'foo', 'b', ('', 'a', 'b', u'é'), autosubmit=True)
        self.assertIn('<select', html)
        self.assertIn('id="foo"', html)
        self.assertIn('onchange="submit()"', html)
        self.assertIn('<option></option>', html)
        self.assertIn('<option>a</option>', html)
        self.assertIn('<option selected="selected">b</option>', html)
        self.assertIn(u'<option>é</option>', html)

        html = Form(DummyRequest()).select('foo', None, (1, 2))
        self.assertIn('<option>1</option>', html)
        self.assertIn('<option>2</option>', html)

        html = Form(DummyRequest()).select(
            'foo', 'b', (('', ''), ('a', 'A'), ('b', 'B'), (u'é', u'É')))
        self.assertIn('<option value="a">A</option>', html)
        self.assertIn('<option selected="selected" value="b">B</option>', html)
        self.assertIn(u'<option value="é">É</option>', html)

        html = Form(DummyRequest()).select(
            'foo', None, ((1, 'One'), (2, 'Two')))
        self.assertIn('<option value="1">One</option>', html)

    # -------------------------------------------------------------------------
    def test_upload(self):
        """[u:lib.form.Form.upload]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).upload('upload_file')
        self.assertIn('type="file"', html)
        self.assertIn('id="upload_file"', html)

    # -------------------------------------------------------------------------
    def test_textarea(self):
        """[u:lib.form.Form.textarea]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).textarea('foo')
        self.assertIn('<textarea', html)
        self.assertIn('id="foo"', html)

    # -------------------------------------------------------------------------
    def test_grid_text(self):
        """[u:lib.form.Form.grid_text]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).grid_text('foo', u'éÔ', clear=True)
        self.assertIn('<div class="formItem">', html)
        self.assertIn('<label for="foo">', html)
        self.assertIn('type="text"', html)
        self.assertIn(u'<em>éÔ</em>', html)
        self.assertIn('<div class="clear">', html)

    # -------------------------------------------------------------------------
    def test_grid_password(self):
        """[u:lib.form.Form.grid_password]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).grid_password('password', 'Password')
        self.assertIn('<div class="formItem">', html)
        self.assertIn('<label for="password">', html)
        self.assertIn('type="password"', html)
        self.assertIn(u'<em>Password</em>', html)
        self.assertNotIn('<div class="clear">', html)

    # -------------------------------------------------------------------------
    def test_grid_checkbox(self):
        """[u:lib.form.Form.grid_checkbox]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).grid_checkbox('foo', u'éÔ')
        self.assertIn('<div class="formItem">', html)
        self.assertIn('<label for="foo">', html)
        self.assertIn('type="checkbox"', html)
        self.assertIn('<label for="foo">', html)

    # -------------------------------------------------------------------------
    def test_grid_custom_checkbox(self):
        """[u:lib.form.Form.grid_checkbox]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).grid_custom_checkbox('foo', u'éÔ')
        self.assertIn('<div class="formItem">', html)
        self.assertIn('wbCustomCheckbox', html)

    # -------------------------------------------------------------------------
    def test_grid_select(self):
        """[u:lib.form.Form.grid_select]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).grid_select(
            'foo', u'éÔ', ('', 'a', 'b', u'é'), autosubmit=True, required=True,
            hint=u'Ôé', clear=True)
        self.assertIn('<div class="formItem">', html)
        self.assertIn('<label for="foo">', html)
        self.assertIn('<select', html)
        self.assertIn('<strong>*</strong>', html)
        self.assertIn('<div class="clear">', html)

    # -------------------------------------------------------------------------
    def test_grid_upload(self):
        """[u:lib.form.Form.grid_upload]"""
        from ..lib.form import Form

        html = Form(DummyRequest()).grid_upload('foo', u'éÔ')
        self.assertIn('<div class="formItem">', html)
        self.assertIn('<label for="foo">', html)
        self.assertIn('type="file"', html)

    # -------------------------------------------------------------------------
    def test_values(self):
        """[u:lib.form.Form.values]"""
        from ..lib.form import Form

        request = DummyRequest()
        request.POST['foo'] = u'éÔ'
        html = Form(request).text('foo')
        self.assertIn(u'value="éÔ"', html)

        form = Form(request)
        form.values['bar'] = u'ôÉ'
        html = form.text('bar')
        self.assertIn(u'value="ôÉ"', html)
