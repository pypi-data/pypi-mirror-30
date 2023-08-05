"""Widget to create tabs."""

from webhelpers2.html import literal


# =============================================================================
class TabSet(object):
    """A class to manages tabs."""

    # -------------------------------------------------------------------------
    def __init__(self, request, labels):
        """Constructor method."""
        self._request = request
        self.labels = labels

    # -------------------------------------------------------------------------
    def toc(self, tab_id):
        """Output a table of content of the ``TabSet`` in an ``<ul>``
        structure.

        :param tab_id: (string)
            Tab set ID.
        :return: (string)
            ``<ul>`` structure.
        """
        translate = self._request.localizer.translate
        xml = '<ul id="%s" class="tabs">\n' % tab_id
        for index, label in enumerate(self.labels):
            xml += '  <li><a class="tab" id="tab%d" href="#tabContent%d">' \
                   '<span>%s</span></a></li>\n' \
                   % (index, index, translate(label))
        xml += '</ul>\n'
        return literal(xml)

    # -------------------------------------------------------------------------
    def tab_begin(self, index, access_key=None):
        """Open a tab zone.

        :param index: (integer)
            Tab index.
        :param access_key: (string, optional)
            Access key for tab.
        :return: (string)
            Opening ``fieldset`` structure with legend.
        """
        return literal(
            '<fieldset class="tabContent" id="tabContent%d">\n'
            '  <legend%s><span>%s</span></legend>\n'
            % (index, access_key and ' accesskey="%s"' % access_key or '',
               self._request.localizer.translate(self.labels[index])))

    # -------------------------------------------------------------------------
    @classmethod
    def tab_end(cls):
        """Close a tab zone."""
        return literal('</fieldset>')
