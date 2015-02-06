import os
import os.path

import whoosh.index

from ..schema import PercsSchema
from .document import PercsDocument
from .common import get_content_hash


class Indexer(object):

    def __init__(self, index_path, force_new=False):
        self.storage_path = index_path
        self.index = self.init_index(force_new)

    @classmethod
    def is_valid_index_dir(cls, path):
        return whoosh.index.exists_in(path)

    @classmethod
    def open_existing(cls, path):
        if os.path.exists(path) and cls.is_valid_index_dir(path):
            return whoosh.index.open_dir(
                path
            )
        else:
            raise ValueError("path not valid index: {0}".format(path))

    def init_index(self, force_new=False):
        create = force_new

        if not os.path.exists(self.storage_path):
            os.mkdir(self.storage_path)
            create = True
        else:
            if not self.is_valid_index_dir(self.storage_path):
                create = True

        if create:
            return whoosh.index.create_in(
                self.storage_path,
                PercsSchema
            )
        else:
            return self.open_existing(self.storage_path)

    def __len__(self):
        return self.index.doc_count()

    def is_empty(self):
        return self.index.is_empty()

    def _index_doc(self, writer, percs_doc):
        expected_fields = self.index.schema.names()

        for page in percs_doc.get_pages():
            index_item = {}
            for field in expected_fields:
                index_item[field] = page[field]
            writer.add_document(**index_item)

    def remove_file(self, filename):
        content_hash = get_content_hash(open(filename, 'rb').read())
        writer = self.index.writer()
        try:
            writer.delete_by_term('file_hash', content_hash)
        except:
            writer.cancel()
            print "Failed to remove: {0} ({1})".format(filename, content_hash)
        else:
            writer.commit()

    def add_items(self, collection, source_directory, name_doc_pairs, progress_callback=None, remove_missing_files=False):
        """ Adds items to the index.

        name_doc_pairs should be iterable, yielding pairs of:
            person: filename

        The filenames should be relative paths to the given
        source_directory.

        The new files will be added to the given collection.

        Will perform an incremental update if possible.

          * Unmodified files won't be re-processed.
          * Modified and new files will be indexed.
          * Deleted files will be removed from the index.
        """
        needs_indexing = set()
        indexed_filenames = set()

        with self.index.searcher() as searcher:
            writer = self.index.writer()

            try:
                for fields in searcher.all_stored_fields():
                    indexed_filename = fields['filename']
                    indexed_filenames.add(indexed_filename)

                    source_filename = os.path.join(
                        source_directory, indexed_filename
                    )

                    if not os.path.exists(source_filename):
                        # File was deleted since last indexing
                        if remove_missing_files:
                            writer.delete_by_term('filename', indexed_filename)
                    else:
                        # Check if the file changed since indexing
                        actual_hash = get_content_hash(
                            open(source_filename, 'rb').read()
                        )
                        known_hash = fields['file_hash']
                        if known_hash != actual_hash:
                            # Delete current index contents
                            writer.delete_by_term('filename', indexed_filename)
                            needs_indexing.add(indexed_filename)
                        else:
                            print("Skipping {0}: \n{1} == {2}".format(
                                source_filename, known_hash, actual_hash
                            ))

                for person, filename in name_doc_pairs:
                    if filename in needs_indexing or filename not in indexed_filenames:
                        doc = PercsDocument(
                            collection,
                            person,
                            os.path.join(
                                source_directory,
                                filename
                            )
                        )
                        self._index_doc(writer, doc)
                        if progress_callback and callable(progress_callback):
                            try:
                                progress_callback(collection, person, filename)
                            except:
                                pass
            except:
                writer.cancel()
                raise
            else:
                writer.commit()


