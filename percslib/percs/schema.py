from whoosh.fields import (
    SchemaClass, STORED, TEXT, ID, DATETIME, NUMERIC
)
from whoosh.analysis import StemmingAnalyzer

class PercsSchema(SchemaClass):
    """ Percs index definition.

    A Whoosh index schema class.  Ultimately the main things
    we want captured:

        * The text content of each page, of each file.
          (eg. When we get a result, we want to know which
            page the result was found.)
        * The name of the person this file is about.
        * The collection in which this file is a member.

    Everything else is just metadata. ;)

        * file content type. Maybe we won't just store PDFs one day?
        * date file was added.
        * possibly the original source of the docs? eg. NSW gov.
    """
    id = ID(stored=True, unique=True)
    collection = ID(stored=True)

    # NOTE: Conceptually, filenames are treated as 'unique'
    #  in the index. However, we treat each page as
    #  the actual index 'documents', so there are multiple
    #  documents with the same filename. This works okay, but
    #  when reindexing a file, we'll need to do every page again,
    #  or identify the specific page that needs updating.
    filename = ID(stored=True)
    page = NUMERIC(stored=True)

    # Keep content hashes, so we can check for modifications.
    # e.g. incremental reindex.
    # Using ID for file_hash, so it's possible to check if a
    # given file has already been added to the index before,
    # without having to trust the filename.
    # I can't see a similar need for the page hash, so
    # sticking with a STORED field (not searchable)...
    #
    # NOTE: Can't flag either of these as unique.
    #   Every page will have the same file_hash, and
    #   potentially, there could be pages with identical
    #   content (eg. "Intentially left blank" heh...)
    file_hash = ID(stored=True)
    page_hash = STORED

    date = DATETIME
    person = TEXT(stored=True)

    # TODO: Add the person's title / seat
    #   Currently when searching for an area, we count on it
    #   being picked up by the content field.  Maybe nice to
    #   have explicit titles added, in case they've handwritten stuff.
    # title = TEXT(stored=True)

    # For now, we're only using PDFs. But, one day... ?
    content_type = ID(stored=True)

    # Can't see an immediate use for this. But easy to capture
    # and is cheap, so ... why not?
    content_length = NUMERIC(stored=True)

    # Use the stemming analyzer, so the user can search
    # for plural/singular, or the 'ing'/'ier'/'ies', etc,
    # versions of each word & still get the hit.
    #
    # Store the content, so we can access hit highlights
    # painlessly (otherwise, will need to fetch from original
    # sources again later).
    content = TEXT(analyzer=StemmingAnalyzer(), stored=True)


