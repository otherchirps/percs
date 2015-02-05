import datetime
import mimetypes
import os
import os.path

from .common import get_content_hash
from .content_handlers import handler_factory

mimetypes.init()


class PercsDocument(object):

    def __init__(self, collection, person, filepath):
        self.collection = collection
        self.person = person
        self._fullpath = filepath
        self.filedir, self.filename = os.path.split(filepath)
        self.date = datetime.datetime.utcnow()
        self.content_type = unicode(mimetypes.guess_type(filepath)[0])
        self.content_length = os.stat(filepath).st_size
        self.load_content()

    def load_content(self):
        if hasattr(self, "_content"):
            return self._content

        handler = handler_factory(self.content_type)
        self._content = handler.get_content(self._fullpath)
        self._page_content = handler.split_pages(self._content)

    @property
    def id(self):
        return self.file_hash

    @property
    def content(self):
        return self._content

    @property
    def file_hash(self):
        result = getattr(self, '_file_hash', None)
        if not result:
            result = get_content_hash(open(self._fullpath, 'rb').read())
            self._file_hash = result
        return result

    def __getitem__(self, name):
        return getattr(self, name, None)

    def get_pages(self):
        if self._page_content is None:
            raise StopIteration
        for page_num, page_content in enumerate(self._page_content, 1):
            yield PercsPage(self, page_num, page_content)


class PercsPage(object):
    """ Provides a PercsDocument interface for one of the given document's
    pages.
    """
    def __init__(self, document, page_num, content):
        self._doc = document
        self.page = page_num
        self.content = content
        self.id = u"{0}-{1}".format(
            self._doc.file_hash,
            self.page
        )
        self.page_hash = get_content_hash(self.content)

    def __getitem__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        return self._doc[name]




