
class ContentHandlerParseError(Exception):
    pass


class BaseContentHandler(object):

    def get_content(self, filename):
        raise NotImplementedError()

    def split_pages(self, content):
        raise NotImplementedError()
