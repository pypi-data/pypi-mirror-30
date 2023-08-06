"""Module for a list of MediaFileLink objects."""
from open_publishing.core import DatabaseObjectsList

from .mediafile_link import MediaFileLink

class MediafileLinkList(DatabaseObjectsList):
    """Class for a list of MediaFileLink objects."""
    _database_object_type = MediaFileLink

    def __init__(self,
                 document):
        """Initialize list of MediaFileLink objects."""
        super(MediafileLinkList, self).__init__(
            database_object=document,
            aspect='mediafile_links',
            list_locator='mediafile_links')
        self._document = document
