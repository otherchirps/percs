from cStringIO import StringIO
import os.path

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

from .base import (
    BaseContentHandler, ContentHandlerParseError
)

class PDFHandler(BaseContentHandler):

    content_type = u'application/pdf'

    def get_content(self, filename):
        if not os.path.exists(filename):
            raise IOError("File not found: {0}".format(filename))

        result = StringIO()
        parser = PDFParser(open(filename, 'r'))

        try:
            document = PDFDocument(parser)
        except Exception, err:
            raise ContentHandlerParseError(str(err))

        if document.is_extractable:
            resource_manager = PDFResourceManager()
            device = TextConverter(
                resource_manager,
                result,
                codec='utf-8',
                laparams = LAParams()
            )
            interpreter = PDFPageInterpreter(resource_manager, device)

            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)

            return unicode(result.getvalue(), 'utf-8')
        else:
            # No extractable text in this file
            return u''


    def split_pages(self, content):
        # Our pdf content is fairly civilized in this case.
        # Form feed chars separate each page.
        # Strip the last entry (caused by terminating form feed)
        return content.split("\f")[:-1]
