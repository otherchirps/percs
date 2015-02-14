import json
from whoosh.qparser import QueryParser
from whoosh import sorting

from indexer import Indexer

DEFAULT_INDEX_DIR = 'percs_idx'


class Searcher(object):

    def __init__(self, index_dir):
        self.index = Indexer.open_existing(index_dir)

    def search(self, query_string, page="1", limit=20):
        results = []
        query_string = unicode(query_string, 'utf-8')
        with self.index.searcher() as searcher:
            query = QueryParser("content", self.index.schema).parse(query_string)

            scores = sorting.ScoreFacet()
            sortperson= sorting.FieldFacet("person")
            sortcollection = sorting.FieldFacet("collection", reverse=True)

            resultset = searcher.search_page(
                query, int(page), pagelen=int(limit),
                sortedby=[sortcollection, scores, sortperson]
            )
            # NOTE: Need to copy plain dicts out, since once the searcher
            #   dies (end of with block), the Hit results lose their reference to
            #   the data.
            for hit in resultset[0:]:
                # Grab a copy of the results as a plain dict.
                result = hit.fields()

                # Also grab the surrounding fragment as a highlight.
                # NOTE: This is pretty much the only point we know
                #   "where" in the matched document the hit occurs.
                #   The raw content we indexed is stored in 'content',
                #   so we tell the Hit instance to pull the surrounding
                #   text fragments from there.
                # Also:
                #   These highlights are pretty much the only reason
                #   we need to bother stashing the entire document.
                #   Otherwise, the index can be even smaller.
                #   Whoosh allows to hunt for the content in the
                #   original files, if they're available.  But as our
                #   text content isn't large -- keeping it in the
                #   index seems faster.
                result['highlights'] = hit.highlights('content')
                results.append(result)

            results = {
                'matches': results,
                'matches_returned': resultset.scored_length(),
                'total_matches': len(resultset),
                'query': query_string
            }
        return results


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Query string")
    parser.add_argument(
        "-i", "--index-dir", dest="index_dir", default=DEFAULT_INDEX_DIR,
        help="Percs index to search against"
    )
    parser.add_argument("-p", "--page", default=1, type=int, help="Page of paginated results to return")
    parser.add_argument("-l", "--limit", default=20, type=int, help="Max number of results to return")
    parser.add_argument("-c", "--contents", default=False, action="store_true",
        help="Return indexed contents with each record"
    )
    args = parser.parse_args()

    s = Searcher(args.index_dir)
    results = s.search(
        query_string=args.query,
        page=args.page,
        limit=args.limit
    )

    if results:
        # Normally the page content we indexed just clutter
        # things up.
        for record in results['matches']:
            if not args.contents:
                del record['content']

    return json.dumps(results, indent=2)

