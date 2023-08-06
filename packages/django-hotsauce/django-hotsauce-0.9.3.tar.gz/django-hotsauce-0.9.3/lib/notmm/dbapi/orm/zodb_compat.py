#!/usr/bin/env python
# -*- coding: utf-8 -*-
from schevo.backends.zodb import ZodbBackend # require zodb 3.7.4
from ._databaseproxy import DatabaseProxy
from threading import local
import logging
log = logging.getLogger(__name__)

__all__ = ['ClientStorageProxy', 'ThreadedConnectionPool']

class ClientStorageProxy(DatabaseProxy):
    def __init__(self, db_name, **kwargs):
        # XXX Hack.
        if not 'db_connection_cls' in kwargs:
            kwargs['db_connection_cls'] = ZodbBackend
        super(ClientStorageProxy, self).__init__(db_name, **kwargs)

class ThreadedConnectionPool(object):
    # pool = ThreadedConnectionPool({
    #    'db1': '127.0.0.1:4343',
    #    'db2': '127.0.0.1:4545',
    # })     
    def __init__(self, d, debug=True):
        if debug:
            assert isinstance(d, dict) == True
        local.pool = d
        for key,value in local.pool.iteritems():
            log.debug("Initializing db: %s" % key)
            local.pool[key] = ClientStorageProxy(value)
        self.pool = local.pool    
    def __getitem__(self, key):
        try:
            v = self.pool[key]
        except KeyError:
            return None
        return v
