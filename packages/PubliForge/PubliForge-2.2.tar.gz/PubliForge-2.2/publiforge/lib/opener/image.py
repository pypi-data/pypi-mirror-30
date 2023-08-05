"""Web image opener."""

import re

from os.path import join, basename, splitext
from webhelpers2.html import literal
from colander import SchemaNode, String
from PIL import Image
from piexif import ImageIFD, dump as exif_dump, load as exif_load

from ...lib.i18n import _
from ...lib.utils import image_metadata
from ...lib.form import Form
from . import Opener as OpenerBase


OVERVIEW_IMAGE_HEIGHT = 48


# =============================================================================
class Opener(OpenerBase):
    """Class to operate on Web images."""
    # pylint: disable = too-many-public-methods

    _config_file = 'image.ini'

    # -------------------------------------------------------------------------
    def match(self, fullname, content=None):
        """Check whether this opener matches with the file ``fullname``.

        See parent method :meth:`Opener.match`.
        """
        self.install_environment()
        regex = self._config_get('Match', 'file_regex')
        if regex and not re.search(regex, fullname):
            return False, content

        return splitext(fullname)[1] in (
            '.jpg', '.jpeg', '.png', '.gif', '.svg'), content

    # -------------------------------------------------------------------------
    def read(self, request, storage, path, content=None):
        """Literal XHTML to display the file content.

        See parent method :meth:`~.lib.opener.Opener.read`.
        """
        # Image without metadata
        extension = splitext(path)[1]
        storage_id = storage['storage_id']
        if extension not in ('.jpg', '.jpeg', '.png', '.gif'):
            return literal(
                u'<div><img src="{path}" alt="{alt}"/></div>'.format(
                    path=request.route_path(
                        'file_download', storage_id=storage_id, path=path),
                    alt=basename(path)))

        # Image with metadata
        metadata = image_metadata(
            join(request.registry.settings['storage.root'], storage_id, path))
        html = u'<div><img src="{path}" alt="{alt}"/>'.format(
            path=request.route_path(
                'file_download', storage_id=storage_id, path=path),
            alt=metadata.get('DocumentName') or basename(path))
        if metadata.get('DocumentName'):
            html += u'<h3 class="imgTitle">{0}</h3>'.format(
                metadata['DocumentName'])
        if metadata.get('ImageDescription'):
            html += u'<div class="imgDescription">{0}</div>'.format(
                metadata['ImageDescription'])
        if metadata.get('Copyright'):
            html += u'<div class="imgCopyright">{0}</div>'.format(
                metadata['Copyright'])
        html += u'<div class="imgInfo">{0}x{1}</div>'.format(*metadata['size'])
        html += u'</div>'
        return literal(html)

    # -------------------------------------------------------------------------
    def overview(self, request, storage, path, content=None):
        """Return an abstract for the current file.

        See parent method :meth:`~.lib.opener.Opener.overview`.
        """
        return \
            u'<img src="{path}" height="{height}" alt="{alt}"/>'.format(
                path=request.route_path(
                    'file_download', storage_id=storage['storage_id'],
                    path=path),
                height=OVERVIEW_IMAGE_HEIGHT, alt=basename(path))

    # -------------------------------------------------------------------------
    def can_write(self):
        """Return ``True`` if it can simply modify the file.

        See parent method :meth:`~.lib.opener.Opener.can_write`.
        """
        self.install_environment()
        return self._config_get('Write', 'can') == 'true'

    # -------------------------------------------------------------------------
    def write(self, request, storage, path, content=None):
        """XHTML form and content for the file to write.

        See parent method :meth:`~.lib.opener.Opener.write`.
        """
        storage_id = storage['storage_id']
        schema = self._vcs_schema(storage)
        schema.add(SchemaNode(String(), name='title', missing=None))
        schema.add(SchemaNode(String(), name='description', missing=None))
        metadata = image_metadata(join(
            request.registry.settings['storage.root'], storage_id, path))
        form = Form(request, schema=schema, defaults={
            'title': metadata.get('DocumentName'),
            'description': metadata.get('ImageDescription')})

        translate = request.localizer.translate
        html = literal(u'<div><img src="{path}" alt="{alt}"/></div>'.format(
            path=request.route_path(
                'file_download', storage_id=storage_id, path=path),
            alt=metadata.get('DocumentName') or basename(path)))
        html += form.grid_text('title', translate(_('Title:')))
        html += form.grid_textarea('description', translate(_('Description:')))
        if 'Copyright' in metadata:
            html += form.grid_item(
                translate(_('Copyright:')), metadata['Copyright'],
                class_='formItem')
        html += form.grid_item(
            translate(_('Size:')), '{0}x{1}'.format(*metadata['size']),
            class_='formItem')

        return form, html, content

    # -------------------------------------------------------------------------
    @classmethod
    def css(cls, mode, request=None):
        """Return a list of CSS files for the mode ``mode``.

        See parent method :meth:`~.lib.opener.Opener.css`.
        """
        # pylint: disable = unused-argument
        return tuple()

    # -------------------------------------------------------------------------
    @classmethod
    def javascript(cls, mode, request=None):
        """Return list of JavaScript files for the mode ``mode``.

        See parent method :meth:`~.lib.opener.Opener.javascript`.
        """
        # pylint: disable = unused-argument
        return tuple()

    # -------------------------------------------------------------------------
    def save(self, request, storage, path, content, values):
        """Reconstitute and save the current file.

        See parent method :meth:`~.lib.opener.Opener.save`.
        """
        # Load image
        filename = join(
            request.registry.settings['storage.root'],
            storage['storage_id'], path)
        try:
            image = Image.open(filename)
        except IOError:
            return False
        if image.format != 'JPEG':
            image.close()
            return False

        # Update metadata
        exif = exif_load(image.info['exif'])
        exif['0th'][ImageIFD.DocumentName] = values['title'].encode('utf8')
        exif['0th'][ImageIFD.ImageDescription] = \
            values['description'].encode('utf8')
        exif['0th'][ImageIFD.ProcessingSoftware] = 'PubliForge'

        # Save file and commit
        handler, user = self._storage_handler(request, storage)
        if handler is None:
            return False
        image.save(filename, 'JPEG', exif=exif_dump(exif))
        image.close()
        handler.add(
            user, path, values.get('message') or
            request.localizer.translate(_('On-line editing')))
        return True

    # def pngsave(im, file):
    #     # these can be automatically added to Image.info dict
    #     # they are not user-added metadata
    #     reserved = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect')

    #     # undocumented class
    #     from PIL import PngImagePlugin
    #     meta = PngImagePlugin.PngInfo()

    #     # copy metadata into new object
    #     for k, v in im.info.iteritems():
    #         if k in reserved:
    #             continue
    #         meta.add_text(k, v, 0)

    #     # and save
    #     im.save(file, "PNG", pnginfo=meta)
