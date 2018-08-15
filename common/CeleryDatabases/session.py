# -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

ResultModelBase = declarative_base()

__all__ = ('SessionManager',)

class SessionManager(object):
    """Manage SQLAlchemy sessions."""

    def __init__(self):
        self.prepared = True

    def get_engine(self, dburi, **kwargs):
        return create_engine(dburi, encoding='utf-8', poolclass=NullPool, **kwargs)

    def create_session(self, dburi, **kwargs):
        engine = self.get_engine(dburi, **kwargs)
        return engine, sessionmaker(bind=engine)

    def prepare_models(self, engine):
        if not self.prepared:
            ResultModelBase.metadata.create_all(engine)
            self.prepared = True

    def session_factory(self, dburi, **kwargs):
        engine, session = self.create_session(dburi, **kwargs)
        self.prepare_models(engine)
        return session()
