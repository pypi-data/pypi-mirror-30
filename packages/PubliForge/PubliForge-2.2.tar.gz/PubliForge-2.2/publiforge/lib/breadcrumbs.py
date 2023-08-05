# -*- coding: utf-8 -*-
"""Breadcrumbs utility."""

from webhelpers2.html import literal

from ..lib.i18n import _


# =============================================================================
class Breadcrumbs(object):
    """User breadcrumb trail, current title page and back URL management.

    This class uses session and stores its history in
    ``session['breadcrumbs']``. It is a list of crumbs. Each crumb is a tuple
    such as ``(<title>, <route_name>, <route_parts>, <chunks_to_compare>)``.
    """

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        self._request = request

    # -------------------------------------------------------------------------
    def trail(self):
        """Output XHTML breadcrumb trail."""
        if 'breadcrumbs' not in self._request.session \
           or len(self._request.session['breadcrumbs']) < 2:
            return literal('&nbsp;')

        translate = self._request.localizer.translate
        crumbs = []
        for crumb in self._request.session['breadcrumbs'][0:-1]:
            if crumb[1] is not None:
                crumbs.append(u'<a href="%s">%s</a>' % (
                    self._request.route_path(crumb[1], **crumb[2]),
                    translate(crumb[0])))
            else:
                crumbs.append(translate(crumb[0]))
        return literal(u' » '.join(crumbs))

    # -------------------------------------------------------------------------
    def current_title(self):
        """Title of current page."""
        if 'breadcrumbs' not in self._request.session \
           or len(self._request.session['breadcrumbs']) < 1 \
           or not self._request.session['breadcrumbs'][-1][1]:
            return _('home')
        return self._request.localizer.translate(
            self._request.session['breadcrumbs'][-1][0])

    # -------------------------------------------------------------------------
    def current_path(self):
        """Path of current page."""
        if 'breadcrumbs' not in self._request.session \
           or len(self._request.session['breadcrumbs']) < 1 \
           or not self._request.session['breadcrumbs'][-1][1]:
            return self._request.route_path('home')
        return self._request.route_path(
            self._request.session['breadcrumbs'][-1][1],
            **self._request.session['breadcrumbs'][-1][2])

    # -------------------------------------------------------------------------
    def back_title(self):
        """Output title of previous page."""
        if 'breadcrumbs' not in self._request.session \
           or len(self._request.session['breadcrumbs']) < 2 \
           or not self._request.session['breadcrumbs'][-2][1]:
            return _('home')
        return self._request.localizer.translate(
            self._request.session['breadcrumbs'][-2][0])

    # -------------------------------------------------------------------------
    def back_path(self):
        """Output the path of previous page."""
        if 'breadcrumbs' not in self._request.session \
           or len(self._request.session['breadcrumbs']) < 2 \
           or not self._request.session['breadcrumbs'][-2][1]:
            return self._request.route_path('home')
        return self._request.route_path(
            self._request.session['breadcrumbs'][-2][1],
            **self._request.session['breadcrumbs'][-2][2])

    # -------------------------------------------------------------------------
    def back_button(self):
        """A button to return to the previous page."""
        return literal(
            u'<a href="{0}" title="{1}">'
            '<img src="/Static/Images/back.png" alt="Back"/></a>'.format(
                self.back_path(), self.back_title()))

    # -------------------------------------------------------------------------
    def add(self, title, length=10, root_chunks=10, replace=None, anchor=None,
            keep=False):
        """Add a crumb in breadcrumb trail.

        :param title: (string)
            Page title in breadcrumb trail.
        :param length: (int, default=10)
            Maximum crumb number. If 0, it keeps the current length.
        :param root_chunks: (int, default=10)
            Number of path chunks to compare to highlight menu item.
        :param replace: (string, optional):
            If current path is ``replace``, this method call :meth:`pop` before
            any action.
        :param anchor: (string, optional)
            Anchor to add.
        :param keep: (boolean, optional)
            If ``True``, keep the last crumb even if it is the same as the
            current.
        """
        # pylint: disable = too-many-arguments
        # Environment
        session = self._request.session
        if 'breadcrumbs' not in session:
            session['breadcrumbs'] = [(_('Home'), 'home', {}, 1)]
        if not length:
            length = len(session['breadcrumbs'])

        # Replace
        if replace and self.current_path() == replace:
            self.pop()

        # Scan old breadcrumb trail to find the right position
        route_name = \
            self._request.matched_route and self._request.matched_route.name
        if route_name is None:
            session['breadcrumbs'].append((title, None, dict(), root_chunks))
            return
        compare_name = route_name.replace('_root', '_browse')\
            .replace('_task', '').replace('_pack', '') + (keep and '_' or '')
        crumbs = []
        for crumb in session['breadcrumbs']:
            crumb_name = crumb[1] and crumb[1].replace('_root', '_browse')\
                .replace('_task', '').replace('_pack', '')
            if len(crumbs) >= length - 1 or crumb_name == compare_name:
                break
            crumbs.append(crumb)

        # Add new breadcrumb
        params = self._request.matchdict
        if anchor is not None:
            params['_anchor'] = anchor
        crumbs.append((title, route_name, params, root_chunks))
        session['breadcrumbs'] = crumbs

    # -------------------------------------------------------------------------
    def pop(self):
        """Pop last breadcrumb."""
        session = self._request.session
        if 'breadcrumbs' in session and len(session['breadcrumbs']) > 1:
            session['breadcrumbs'] = session['breadcrumbs'][0:-1]
