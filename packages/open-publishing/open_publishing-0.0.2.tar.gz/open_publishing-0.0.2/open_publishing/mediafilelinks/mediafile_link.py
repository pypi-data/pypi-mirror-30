"""Module for GJP abstraction of media file links."""

from open_publishing.core import SimpleField
from open_publishing.core import FieldDescriptor
from open_publishing.core import DatabaseObject
from open_publishing.core.enums import MediaFileTypeCode, MediaFileFormatCode, MediaFileLinkTypeCode

class MediaFileLink(DatabaseObject):
    """Class for GJP abstraction of media file links."""
    _object_class = 'document_mediafile_link'

    def __init__(self,
                 context,
                 mediafile_link_id):
        """Initalize a media file link."""
        super(MediaFileLink, self).__init__(context,
                                            mediafile_link_id)

        self._fields['url'] = SimpleField(
            database_object=self,
            aspect='*',
            field_locator='media_file_link',
            dtype=str)

        self._fields['type_code'] = SimpleField(
            database_object=self,
            aspect='*',
            field_locator='media_file_type_code',
            dtype=MediaFileTypeCode)

        self._fields['format_code'] = SimpleField(
            database_object=self,
            aspect='*',
            field_locator='media_file_format_code',
            dtype=MediaFileFormatCode,
            nullable=True)

        self._fields['link_type_code'] = SimpleField(
            database_object=self,
            aspect='*',
            field_locator='link_type_code',
            dtype=MediaFileLinkTypeCode)

        self._fields['publication_type'] = SimpleField(
            database_object=self,
            aspect='*',
            field_locator='publication_type',
            dtype=str)

    url = FieldDescriptor('url')
    type_code = FieldDescriptor('type_code')
    format_code = FieldDescriptor('format_code')
    link_type_code = FieldDescriptor('link_type_code')
    publication_type = FieldDescriptor('publication_type')

    @property
    def mediafile_link_id(self):
        """Property for media file link id."""
        return self._object_id
