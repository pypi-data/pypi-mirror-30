#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notmm.controllers.session import SessionController
from notmm.dbapi.orm.zodb_compat import ClientStorageProxy

import logging
logger = logging.getLogger('notmm.controllers.wsgi')

__all__ = ['ZODBController']

class ZODBController(SessionController):

    backendClass = ClientStorageProxy
    key_prefix = 'schevo.db.'

    def __init__(self, request, db_name, **kwargs):
        super(ZODBController, self).__init__(**kwargs)
        self.environ_key = self.key_prefix + 'zodb'
        self.db_name = db_name
        self.setup_database(db_name)
        
    def setup_database(self, db_name):
        self.db = self.backendClass(db_name)

    def init_request(self, environ):
        super(ZODBController, self).init_request(environ)
        
        if self.debug:
            assert self.environ_key == 'schevo.db.zodb' # XXX use settings.SCHEVO['DATABASE_URL']

        self.request.environ[self.environ_key] = self.db
        return self.request
