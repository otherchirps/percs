""" Percs indexer command line util.

    Currently fairly limited & specific for the current incarnation of percs..

    * Assumes we're only doing pdfs (which we are, for now),
    * Assumes the 'name' we're using (eg. the minister's name) is
      embedded in the pdf's Subject metadata field (will be if percs-pdf-split was used).
"""

import argparse
import csv
import datetime
import os
import os.path

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from .indexer import Indexer


def get_pdf_subject(pdf_filename):
    with open(pdf_filename, 'rb') as pdf_file:
        parser = PDFParser(pdf_file)
        doc = PDFDocument(parser)
        info = doc.info[0]
        return info.get('Subject', None)

def get_index_name_doc_pairs(directory, name_csv=None):
    names = {}
    if name_csv and os.path.exists(name_csv):
        # Expecting rows like: name,filename
        with open(name_csv, 'r') as namefile:
            csv_rows = csv.reader(namefile)
            for row in csv_rows:
                names[row[1]] = row[0]

    for root_dir, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            base, ext = os.path.splitext(filename)
            if ext.lower() != ".pdf":
                continue

            name = names.get(filename, None)
            if not name:
                name = get_pdf_subject(
                    os.path.join(root_dir, filename)
                )
            if not name:
                raise Exception("Name not found for: " + filename)
            yield unicode(name, 'utf-8'), unicode(filename, 'utf-8')

def report_progress(*args, **kwargs):
    print("Indexed: {0}\n".format(str(args)))

def run():
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('directory', help="Directory path containing PDFs to be indexed")
    cli_parser.add_argument('-i', '--index-dir', dest="index_dir", help="Index directory. Default: CURRENT_DIR/percs_idx")
    cli_parser.add_argument('-f', '--force-new', dest="force_new", action="store_true", default=False, help="If index dir is an existing index, clear and create a new index in its place")
    cli_parser.add_argument('-c', '--collection-name', dest="collection", help="Collection name for indexed files. Default to current date (yyyy-mm-dd)")
    cli_parser.add_argument('-n', '--name-csv', dest='name_csv', help="Load names from csv, instead of embedded pdf metadata. Expects (name, filename) rows")
    cli_parser.add_argument('-r', '--remove-missing', dest='remove_missing', default=False, action="store_true", help="Remove missing files from the index, when indexing a directory")
    cli_parser.add_argument('-s', '--size', default=False, action="store_true", help="Show number of records in index, and exit")

    args = cli_parser.parse_args()
    collection = args.collection or datetime.date.today().isoformat()

    indexer = Indexer(args.index_dir, args.force_new)

    if args.size:
        count = indexer.index.doc_count()
        print("Records in {0} index: {1}".format(
            args.index_dir, count
        ))
        return

    indexer.add_items(
        unicode(collection, 'utf-8'),
        unicode(args.directory, 'utf-8'),
        get_index_name_doc_pairs(args.directory, args.name_csv),
        report_progress,
        args.remove_missing
    )

if __name__ == "__main__":
    run()

