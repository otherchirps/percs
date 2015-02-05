import unittest
import os
import os.path
import shutil

from percs.indexer import Indexer


class TestIndexer(unittest.TestCase):

    def setUp(self):
        self.root_dir = os.path.dirname(__file__)
        self.index_dir = "tmp_index_" + self.__class__.__name__
        self.fixture_dir = os.path.join(
            self.root_dir,
            'fixtures'
        )
        self.sample_pdf_filename = os.path.join(
            self.fixture_dir,
            'sample.pdf'
        )

    def tearDown(self):
        if os.path.exists(self.index_dir):
            shutil.rmtree(self.index_dir)

    def test_can_create_index(self):
        indexer = Indexer(self.index_dir)
        self.assertTrue(
            os.path.exists(self.index_dir),
            "Failed to create index storage"
        )
        self.assertTrue(
            indexer.is_valid_index_dir(self.index_dir)
        )

    def test_can_add_document(self):
        indexer = Indexer(self.index_dir)

        source_dir, filename = os.path.split(self.sample_pdf_filename)
        name_pairs = (
            (u'test sample name', unicode(filename, 'utf-8')),
        )

        indexer.add_items(
            u'test_collection',
            source_dir,
            name_pairs
        )

        self.assertGreater(len(indexer), 0, "No documents added to index")

