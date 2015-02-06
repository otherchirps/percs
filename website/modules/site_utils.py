import math
import os
import os.path
from gluon import DIV, A, UL, LI, I

def pager(total_records, page_limit, current_page, target_url, page_var):
    """ Generates a simple pagintator navigation block.
    """
    total_pages = int(math.ceil(total_records/float(page_limit)))
    current_page = int(current_page)

    if total_pages <= 1:
        return None

    prev_disabled = current_page <= 1
    next_disabled = current_page == total_pages

    # Build the page links...
    url_fmt = target_url
    # Any other query params?
    if '?' in url_fmt:
        url_fmt += '&'
    else:
        url_fmt += '?'
    url_fmt += page_var + '={0}'

    result = DIV(_class="pagination")
    page_list = UL()

    prev_page = LI()
    next_page = LI()

    if prev_disabled:
        prev_page['_class'] = "disabled"
        prev_page.append(A(I(_class="icon-backward"), _href="#"))
    else:
        prev_page.append(
            A(I(_class="icon-backward"), _href=url_fmt.format(current_page-1))
        )

    if next_disabled:
        next_page['_class'] = 'disabled'
        next_page.append(A(I(_class="icon-forward"), _href="#"))
    else:
        next_page.append(
            A(I(_class="icon-forward"), _href=url_fmt.format(current_page+1))
        )

    page_list.append(prev_page)

    for page_num, idx in enumerate(xrange(total_pages), 1):
        entry = LI(
            A(str(page_num), _href=url_fmt.format(page_num))
        )
        if page_num == current_page:
            entry['_class'] = "active"
        page_list.append(entry)

    page_list.append(next_page)
    result.append(page_list)

    return result

_collections = None

def _get_collection_path(app_path, collection=''):
    collection = collection.replace('..', '')

    return os.path.join(app_path, 'static', 'collections', collection)

def get_collections(app_path):
    global _collections
    if _collections:
        return _collections

    _collections = os.listdir(
        os.path.join(app_path, 'static', 'collections')
    )
    _collections.sort(reverse=True)

    return _collections

def get_docs(app_path, collection):
    collection_path = _get_collection_path(app_path, collection)

    for filename in os.listdir(collection_path):
        if filename.lower().endswith(".pdf"):
            yield filename

def get_collection_desciption(app_path, collection):
    collection_path = _get_collection_path(app_path, collection)

    description = os.path.join(collection_path, 'README')
    if os.path.exists(description):
        try:
            return open(description, 'r').read().strip()
        except:
            return ''
