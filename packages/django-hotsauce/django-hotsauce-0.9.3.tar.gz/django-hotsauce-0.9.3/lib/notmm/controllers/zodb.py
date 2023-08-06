#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notmm.controllers.session import SessionController
from notmm.utils.django_settings import LazySettings
import logging
logger = logging.getLogger('notmm.controllers.wsgi')

_settings = LazySettings()

_default_manager = _settings.SCHEVO['connection_manager']

__all__ = ['ZODBController']

class ZODBController(SessionController):

    key_prefix = 'schevo.db.'

    def __init__(self, request, db_name, manager=_default_manager, **kwargs):
        super(ZODBController, self).__init__(**kwargs)
        self.environ_key = self.key_prefix + 'zodb'
        self.db_name = manager[db_name]

        self.setup_database(db_name)
        
    def setup_database(self, db_name, fallback_db='db1'):
        try:
            self.db = getattr(_default_manager, db_name)
        except AttributeError:
            self.db = _default_manager[fallback_db]

    def init_request(self, environ):
        request = super(ZODBController, self).init_request(environ)
        if self.debug:
            assert self.environ_key == 'schevo.db.zodb' # XXX use settings.SCHEVO['DATABASE_URL']

        request.environ[self.environ_key] = self.db
        return request
