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
        sql = "INSERT INTO fail_tasks(hostname,queue,type, \
                 taskname, taskid, payload, exception, trace, stime, ctime) \
               VALUES ('%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )" % \
              (hostname, queue, type, taskname, taskid, payload, excep, trace, newstime, ctime)
        self.recordTaskInfo(sql,queue,payload,trace,type)


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
        sql = "INSERT INTO fail_tasks(hostname,queue,type, \
                         taskname, taskid, payload, exception, trace, stime, ctime) \
                       VALUES ('%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )" % \
              (hostname, queue, type, taskname, taskid, payload, excep, trace, newstime, ctime)
        self.recordTaskInfo(sql,queue,payload,trace,type)

    def on_success(self, failed__retval__runtime, **kwargs):
        super(MyRequest, self).on_success(self, failed__retval__runtime, **kwargs)
        failed, retval, runtime = failed__retval__runtime
        # logger.info(failed__retval__runtime)
        # logger.info("000000000000000000000")
        # logger.info(failed)
        # logger(failed__retval__runtime)
        # raise Exception('pppppppppppppppp')

    def recordTaskInfo(self, sql,queue,payload,trace,type):
        CDatabase = CeleryDatabases()
        conn = CDatabase.getConnect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SET NAMES utf8;')
                cursor.execute('SET CHARACTER SET utf8;')
                cursor.execute('SET character_set_connection=utf8;')
                cursor.execute(sql)
                conn.commit()
        except Exception as e:
            logger.error("save failure task failure: queue:"+queue
                         +"---payload: "+payload
                         +"---trace: "+trace
                         +"---type: " +str(type))
        finally:
            conn.close()
            del conn
            del CDatabase

    def decodeHtml(self, input):
        s = html.escape(input)
        return s

class Ctask(celery.Task):
    Request = MyRequest
    # def on_success(self, retval, task_id, args, kwargs):
    #     super(Ctask, self).on_success(retval, task_id, args, kwargs)
    #     # logger.info(failed__retval__runtime)
    #     logger.info("000000000000000000000")
    #     logger.info(retval)
    #     logger.info(task_id)
    #     logger.info(args)
    #     logger.info(kwargs)
        # logger.info(self.request)
