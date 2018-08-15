# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import html
import celery
import datetime

from celery.worker.request import Request
from celery.utils.log import get_task_logger
from kombu.utils.encoding import safe_repr, safe_str
from CeleryDatabases.CeleryDatabases import CeleryDatabases

logger = get_task_logger(__name__)
class MyRequest(Request):

    def on_retry(self, exc):
        super(MyRequest, self).on_retry(exc)
        hostname = safe_str(self.hostname)
        queue = safe_str(self.delivery_info.get('routing_key'))
        taskname = safe_str(self.task.name)
        taskid = safe_str(self.id)
        payload = self.argsrepr
        payload = self.decodeHtml(payload)
        excep = safe_repr(exc.exception)
        excep = self.decodeHtml(excep)
        trace = safe_str(exc.traceback)
        trace = self.decodeHtml(trace)
        stime = self.info()['time_start']
        newstime = datetime.datetime.fromtimestamp(stime)
        ctime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        type = 1
        CDatabase = CeleryDatabases()
        CDatabase.inster_fail_task(hostname, queue, type, taskname, taskid, payload, excep, trace, newstime, ctime)


    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        super(MyRequest, self).on_failure(
            exc_info,
            send_failed_event=send_failed_event,
            return_ok=return_ok
        )

        hostname = safe_str(self.hostname)
        queue = safe_str(self.delivery_info.get('routing_key'))
        taskname = safe_str(self.task.name)
        taskid = safe_str(self.id)
        payload = self.argsrepr
        payload = self.decodeHtml(payload)
        excep = safe_repr(exc_info.exception)
        excep = self.decodeHtml(excep)
        trace = safe_str(exc_info.traceback)
        trace = self.decodeHtml(trace)
        stime = self.info()['time_start']
        newstime = datetime.datetime.fromtimestamp(stime)
        ctime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        type = 2
        CDatabase = CeleryDatabases()
        CDatabase.inster_fail_task(hostname, queue, type, taskname, taskid, payload, excep, trace, newstime, ctime)

    def decodeHtml(self, input):
        s = html.escape(input)
        return s

class Ctask(celery.Task):
    Request = MyRequest
