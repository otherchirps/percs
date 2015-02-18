import argparse
from collections import namedtuple
import csv
import os
import os.path
import urllib

from PyPDF2 import (
    PdfFileReader, PdfFileWriter
)


class PageRange(namedtuple("PageRange", ["start_page",
                                         "end_page",
                                         "name",
                                         "output_filename"])):
    """ A namedtuple, with optional filename param.
    """
    def __new__(cls, start_page, end_page, name, output_filename=None):
        return super(PageRange, cls).__new__(
            cls, int(start_page), int(end_page), name, output_filename
        )


class PDFSplitter(object):
    """ Creates pdf files with subsets of pages of the given original.
    """

    def split(self, original_filename, page_ranges, output_dir=None):
        """
        Expects page_ranges to return an iterable sequence containing:

            (start_page, end_page, name, output filename)

        Where start_page & end_page are 1-based indexes.
        This is to help line up with data-entry form a pdf-viewer, which normally
        displays the first page as "page 1".

        The `name` will be embedded as the pdf's Subject metadata field.
        This allows us to store names with crazy characters, and not have to
        worry how the filename is mutated, to allow for urlencoding, etc.

        The output filename is optional.  If not given, the new pdfs will have the
        original filename with a numerical prefix added before the file extension.

        :param str original_filename: Filename of the original PDF to be split.

        :param iterable page_ranges: Provides sequences of start_page, end_page,
            and optionally, output filename. start_page and end_page should be
            integers, being 1-based page numbers of the original pdf.
        """
        path, filename = os.path.split(original_filename)
        if not output_dir:
            output_dir = os.getcwd()
        filename_base, filename_ext = os.path.splitext(filename)

        with open(original_filename, 'rb') as orig_pdf:
            pdf_reader = PdfFileReader(orig_pdf)
            max_page = pdf_reader.getNumPages()

            for output_num, page_range in enumerate(page_ranges):
                if not isinstance(page_range, PageRange):
                    page_range = PageRange(*page_range)

                if page_range.output_filename:
                    output_filename = os.path.join(
                        output_dir, page_range.output_filename
                    )
                else:
                    output_filename = os.path.join(
                        output_dir,
                        "{0}_{1}{2}".format(
                            filename_base,
                            output_num,
                            filename_ext
                        )
                    )

                # Handle name collisions...
                if os.path.exists(output_filename):
                    os.remove(output_filename)

                # Walk the given page_ranges & create new sub-pdfs.
                with open(output_filename, "wb") as output_pdf:
                    pdf_writer = PdfFileWriter()
                    pdf_writer.addMetadata({"/Subject": page_range.name})

                    # PdfFileReader uses 0-based indexing
                    first = max(0, page_range.start_page - 1)
                    last = min(max_page, page_range.end_page)

                    for page_idx in xrange(first, last):
                        pdf_writer.addPage(
                            pdf_reader.getPage(page_idx)
                        )

                    pdf_writer.write(output_pdf)
                    pdf_writer = None

    def split_with_csv(self, original_filename, csv_page_range_filename, header_row=False, output_dir=None):
        """ Splits pdf, as with `split`, but loads page_ranges from csv.

        :param str original_filename: Filename of original PDF to be split.

        :param str csv_page_range_filename: CSV file containing page ranges.

        :param bool header_row: Should be True if the first CSV row is a
            header row to be skipped.
        """
        with open(csv_page_range_filename, "r") as csv_file:
            range_reader = csv.reader(csv_file)
            if header_row:
                range_reader.next()
            page_ranges = (
                PageRange(*row)
                for row in range_reader
            )
            self.split(original_filename, page_ranges, output_dir)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help="PDF file to split")
    parser.add_argument('-c', '--csv-page-ranges', dest='csv_filename', help="CSV containing start, end, name & (optional) output filename for range")
    parser.add_argument('-o', '--output-directory', dest='output_dir', help="Output directory. Default: current directory")
    parser.add_argument('-H', '--header-row', action="store_true", dest="header_row", default=False, help="CSV contains header row to skip")

    args = parser.parse_args()

    splitter = PDFSplitter()
    splitter.split_with_csv(
        args.filename, args.csv_filename,
        args.header_row, args.output_dir
    )


if __name__ == "__main__":
    run()


