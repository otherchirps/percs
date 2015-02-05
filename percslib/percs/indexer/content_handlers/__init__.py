
from .pdf_handler import PDFHandler


_handlers = {
    handler.content_type: handler
    for handler in [
        PDFHandler,
        # Other type handler classes here... one day...
    ]
}

def handler_factory(content_type):
    handler =  _handlers.get(content_type, None)
    if handler:
        return handler()
