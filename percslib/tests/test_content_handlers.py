import unittest

from percs.indexer.content_handlers import (
    handler_factory, PDFHandler
)

class TestHandlerFactory(unittest.TestCase):

    def test_pdf_type_gets_pdf_handler(self):
        handler = handler_factory(u'application/pdf')
        self.assertIsInstance(handler, PDFHandler, "Incorrect handler found")
