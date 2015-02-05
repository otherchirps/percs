# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = T('doc search') # ' '.join(word.capitalize() for word in request.application.split('_'))
response.subtitle = '' # T('2013-2014 for now...')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Christopher Nilsson <christopher@otherchirps.net>'
response.meta.description = 'indexing pdfs...'
response.meta.keywords = 'nsw,government,declared interests'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = 'UA-9567489-9'

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################
response.menu = []

#response.menu = [
#    (T('Home'), False, URL('default','index'), [])
#    ]

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu+=[
        (T('Collections'), False, URL('default', 'collections'), []),
        (T('About'), False, URL('default','about'), [])
    ]

_()

