.. _implementation:

Implementation
==============

The original PDFs were run through `Tesseract`_, using `PyPDFOCR`_.  
The text content was then indexed using `PDFMiner`_, `Whoosh`_.

OCR and indexing is done offline. The static index is then served by the website.

The percslib python package can, and probably should, be split off into its own project, as it
can split, index, and search independantly of the little website tacked in front of it.
Maybe one day...

Why do it this way?
-------------------

When there are very cool open source search platforms, like `Elasticsearch`_ and `Solr`_,
which *already* index PDFs out of the box?

Hosting cost.

The aim was to not only index the text, but make it available for near zero cost.  Servers which
can handle the OCR processing (lots of CPU...), or an Elasticsearch/Solr instance (lots of memory...),
don't cost near to nothing.

The current implementation means it can be thrown onto tiny shared hosts
without a worry.

Plus, `Whoosh`_ kicks ass!

.. _Tesseract: https://code.google.com/p/tesseract-ocr/
.. _PyPDFOCR: https://pypi.python.org/pypi/pypdfocr
.. _PDFMiner: https://pypi.python.org/pypi/pdfminer/
.. _Whoosh: https://pypi.python.org/pypi/Whoosh
.. _Elasticsearch: http://www.elasticsearch.com/
.. _Solr: http://lucene.apache.org/solr/ 

