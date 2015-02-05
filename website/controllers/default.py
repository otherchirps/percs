# -*- coding: utf-8 -*-

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

import os.path
import urllib

import percs
import percs.search
from percs.search import Searcher

from site_utils import (
    pager, get_collections, get_docs, get_collection_desciption
)

INDEX_DIR = "percs_idx"


def index():
    """ Landing page
    """
    query = request.vars.get('query', None)
    if not query:
        return dict(message='')
    else:
        searcher = Searcher(
            os.path.join(request.folder, 'private', INDEX_DIR)
        )
        page = request.vars.get('page', 1)
        limit = request.vars.get('limit', 20)
        results = searcher.search(query, page, limit)
        if results:
            records = results['matches']
            pagelen = results['matches_returned']
            total = results['total_matches']
        else:
            records, pagelen, total = None, None, None

        for record in records:
            # Normalize the chars our webserver chokes on.
            # Security!!  (╯°□°）╯︵ ┻━┻
            #
            # NOTE: I've already renamed the guilty files,
            #   but keeping just in case any creep back...
            filename = record['filename'].replace("'","-").replace(", ", "_")

            # We also need to disable the automatic urlencoding here.
            # Since, by default, it'll encode our pdf open flags
            # (eg. #page=X). So, we'll explicitly quote_plus the
            # url, but add # and = to the ignore list.
            record['download_path'] = URL(
                'static',
                'collections/{0}/{1}'.format(
                    urllib.quote_plus(record['collection']),
                    urllib.quote_plus(filename, '#=')
                ),
                url_encode=False
            )
        return dict(
            message='',
            results=records,
            pagelen=pagelen,
            total=total,
            limit=limit,
            page=page,
            query=query,
            paginator=pager(
                total, limit, page,
                URL(vars=dict(limit=limit, query=query)),
                "page"
            )
        )

def about():
    return dict()

def collections():
    collection = None
    available_collections = get_collections(request.folder)

    if request.args and request.args[0] in available_collections:
        collection = request.args[0]
        filenames = list(get_docs(request.folder, collection))
        filenames.sort()
        description = get_collection_desciption(request.folder, collection)
        if description:
            description = MARKMIN(description)
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
