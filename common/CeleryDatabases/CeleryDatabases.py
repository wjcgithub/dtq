# -*- coding: utf-8 -*-
from __future__ import absolute_import

from contextlib import contextmanager

from .session import SessionManager
from celeryConfig import mysqlconfig as config
from clog.clog import logger
from .Models.Groups import Groups
from .Models.Queues import Queues
from .Models.FailTasks import FailTasks
from .Models.WorkConfig import WorkConfig


class CeleryDatabases(object):

    def __init__(self):
        self.engine_options = {}
        self.url = 'mysql://%s:%s@%s:3306/%s' % (config.db_user, config.db_pass, config.db_host, config.db_name)

    @contextmanager
    def session_cleanup(self,session):
        try:
            yield
        except Exception as exc:
            session.rollback()
            logger.error('Thread Timer crashed: %r', exc, exc_info=True)
            raise
        finally:
            session.close()


    def getSession(self, session_manager=SessionManager()):
        """Get mysql session"""
        return session_manager.session_factory(
            dburi=self.url,
            **self.engine_options)

    def get_group_by_status(self,gid=None,return_one=False,status=None):
        """Get group meta-data for a group by id."""
        session = self.getSession()
        q = session.query(Groups)
        with self.session_cleanup(session):
            if gid is not None:
                q = q.filter(Groups.id == gid)

            if status is not None:
                q = q.filter(Groups.status == status)

            rest = q.first() if return_one else q.all()
            if rest:
                return rest

        return None

    def get_queue_by_status(self,qid=None,gid=None,return_one=False,status=None):
        """Get queue meta-data for a queue by id."""
        session = self.getSession()
        q = session.query(Queues)
        with self.session_cleanup(session):
            if qid is not None:
                q = q.filter(Queues.id == qid)

            if gid is not None:
                q = q.filter(Queues.gid == gid)

            if status is not None:
                q = q.filter(Queues.status == status)

            rest = q.first() if return_one else q.all()
            if rest:
                return rest

        return None

    def get_workerconfig(self):
        """Get work config."""
        session = self.getSession()
        with self.session_cleanup(session):
            rest = session.query(WorkConfig).all()
            if rest:
                return rest

        return None

    def inster_fail_task(self,hostname, queue, type, taskname, taskid, payload, excep, trace, newstime, ctime):
        """Get work config."""
        session = self.getSession()
        with self.session_cleanup(session):
            Obj = FailTasks(
                hostname=hostname,
                queue=queue,
                type=type,
                taskname=taskname,
                taskid=taskid,
                payload=payload,
                exception=excep,
                trace=trace,
                stime=newstime,
                ctime=ctime
            )
            session.add(Obj)
            session.commit()
        return True