# _*_ coding:utf-8 _*_
from __future__ import absolute_import

import os

from common.CeleryDatabases.CeleryDatabases import CeleryDatabases
from common.clog.clog import logger
from common.celeryConfig import pconfig as pconfig

class CeleryConfigFile(object):
    __projectsConfig = {}
    __rootPath = ''
    __programsPath = ''
    __supervisorConfPath = ''

    def __init__(self):
        self.__initConfig()

    def __initConfig(self):
        # init from config
        self.__projectsConfig['rootpath'] = pconfig.rootpath
        self.__projectsConfig['programs'] = os.path.join(pconfig.rootpath,'programs')
        self.__projectsConfig['celery_log_path'] = os.path.join(pconfig.rootpath,'log')

        # init from database
        sql = 'select name,value from worker_config'
        cDatabase = CeleryDatabases()
        configDic = cDatabase.execute_query(sql, return_one=False)
        if configDic:
            for one in configDic:
                self.__projectsConfig[one['name']] = one['value']

    def checkConfig(self, group=None, queue=None, gid=0, queueid=0, groupname=''):
        if(self. hasGroup(group)):
            self.__deleteConfig(group=group, queue=queue)

        self.__generalConfig(group, queue, gid, queueid, groupname)

    def supervisorRestart(self):
        logger.info(os.system('supervisorctl reread'))
        logger.info(os.system('supervisorctl update'))

    def supervisorRestartGroup(self,groupname):
        logger.info(os.system('supervisorctl update '+groupname))

    def hasGroup(self, group):
        if(os.path.exists(os.path.join(self.__projectsConfig['programs'],group))):
            return True
        else:
            return False

    def __deleteConfig(self, group=None, queue=None):
        self.__celeryRemoveDir(os.path.join(self.__projectsConfig['programs'],group,queue))
        self.__celeryRemoveDir(os.path.join(self.__projectsConfig['celery_log_path'],group,queue))
        supervisorFile = os.path.join(pconfig.supervisor_config_path, group+'_'+queue+'_worker.'+pconfig.super_file_suffix)
        if(os.path.exists(supervisorFile)):
            os.remove(supervisorFile)

        logger.info('delete queue %s of %s group success' % (queue,group))

    def __celeryRemoveDir(self, dirPath=''):
        if not os.path.isdir(dirPath):
            return
        files = os.listdir(dirPath)
        try:
            for file in files:
                filePath = os.path.join(dirPath, file)
                if os.path.isfile(filePath):
                    os.remove(filePath)
                elif os.path.isdir(filePath):
                    self.__celeryRemoveDir(filePath)
            os.rmdir(dirPath)
        except Exception as e:
            logger.error('查询数据错误:%s' % (e))

    def __generalConfig(self, group=None, queue=None, gid=0, queueid=0, groupname=''):
        cDatabase = CeleryDatabases()
        #查询队列详情
        sql = 'select * from queues where id=%s' % (queueid)
        queueDic = cDatabase.execute_query(sql, return_one=True)
        #查询该组中的所有队列
        # sql = 'select name from queues where gid=%d' % (gid)
        # queueNameDic = cDatabase.execute_query(sql)
        # qnameStr = ''
        # for qname in queueNameDic:
        #     qnameStr+=qname['name']
        #     qnameStr+=','
        #组装路径
        groupPath = os.path.join(self.__projectsConfig['programs'],group)
        queuePath = os.path.join(self.__projectsConfig['programs'],group,queue)
        celeryConfigDir = os.path.join(self.__projectsConfig['programs'],group,queue,'celeryconfig')
        supervisorFile = os.path.join(pconfig.supervisor_config_path, group+'_'+queue+'_worker.'+pconfig.super_file_suffix)
        celeryLogPath = os.path.join(self.__projectsConfig['celery_log_path'],group,queue)
        os.makedirs(queuePath)
        os.makedirs(celeryConfigDir)
        os.makedirs(celeryLogPath)
        self.__touchFile(os.path.join(groupPath,'__init__.py'),'')
        self.__touchFile(os.path.join(queuePath,'__init__.py'),'')
        self.__touchFile(os.path.join(celeryConfigDir,'__init__.py'),'')
        celeryConfigFile = """broker_url='%s'
result_backend='%s'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
include = ['%s.task']
task_queues = {
    '%s': {
        'exchange': '%s',
        'routing_key': '%s',
    },
}
task_routes = {
    '%s.task.handler': {'queue': '%s', 'exchange': '%s', 'routing_key': '%s'},
}
result_expires = 3600
# result_persistent = True
task_time_limit = 5
task_soft_time_limit = 3
worker_max_tasks_per_child = 8000
worker_max_memory_per_child = 50000
task_acks_late = True
task_reject_on_worker_lost = True   # Warning Enabling this can cause message loops; make sure you know what you're doing
worker_prefetch_multiplier = 0
worker_pool_restarts = True
task_ignore_result = False
task_store_errors_even_if_ignored = True
worker_enable_remote_control=True
worker_state_db='%s'
""" % (self.__projectsConfig['broker_url']+self.__projectsConfig['exchange'],
       self.__projectsConfig['result_backend'],
       queue,
       group+'_'+queue,
       self.__projectsConfig['exchange'],
       group+'_'+queue,
       queue,
       group+'_'+queue,
       self.__projectsConfig['exchange'],
       group + '_' + queue,
       os.path.join(self.__projectsConfig['celery_log_path'],group,queue,queue)
       )
        self.__touchFile(os.path.join(celeryConfigDir,'celeryconfig.py'),celeryConfigFile)

        # touch celery.py
        celeryFile = """#!/usr/bin/env python3.5
# _*_ coding:utf-8 _*_
from __future__ import absolute_import, unicode_literals
from celery import Celery
import %s.celeryconfig.celeryconfig as celeryconfig
import sys
import os

sys.path.append(os.path.abspath('../../')+'/common')

app = Celery('%s')
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()""" % (queue,queue)
        self.__touchFile(os.path.join(queuePath,'celery.py'),celeryFile)
        # os.chmod(os.path.join(queuePath,'celery.py'),777)

        # touch task.py
        taskFile = """from __future__ import absolute_import, unicode_literals

import errno
import requests
import json

from celery.exceptions import Reject
from %s.celery import app
from CeleryCustomTask.CeleryCustomTask import Ctask

@app.task(
          base=Ctask,
          bind=True,
          )
def handler(self, payload):
    try:
        url = '%s'
        r= requests.post(url,{'payload':payload},timeout=%d)
        r.raise_for_status()
        data = {"queuename":"%s", "payload":payload}
        return json.dumps(data)
    except MemoryError as exc:
        raise Reject(exc, requeue=True)
    except OSError as exc:
        if exc.errno == errno.ENOMEM:
            raise Reject(exc, requeue=True)
    except Exception as exc:
        self.retry(countdown=3, exc=exc, max_retries=3)
        """ % (queue, queueDic['callback_url'],queueDic['timeout'],group+'_'+queue)
        self.__touchFile(os.path.join(queuePath, 'task.py'), taskFile)

        # touch supervisor file
        supervisor = """[program:%s]
command=celery --app=%s worker -l info -Ofair -n %s.%%%%h.%%(process_num)d -Q %s -c %d -f %s
directory=%s
user=celery
numprocs=%d
process_name=%%(program_name)s%%(process_num)d@%%(host_node_name)s
numprocs_start=1
stdout_logfile=%s
stderr_logfile=%s
stdout_logfile_backups = 10
stderr_logfile_backups = 10
stdout_logfile_maxbytes = 50MB
stderr_logfile_maxbytes = 50MB
autostart=true
autorestart=true
startsecs=3
stopwaitsecs = 600 
stopasgroup=true
priority=%d

[group:%s]
programs=%s
        """ % (group+'_'+queue,
               queue,
               group+'_'+queue,
               group+'_'+queue,
               queueDic['concurrency'],
               os.path.join(self.__projectsConfig['celery_log_path'],group,queue+'_worker_out.log'),
               os.path.join(self.__projectsConfig['programs'], group),
               int(self.__projectsConfig['numprocs']),
               os.path.join(self.__projectsConfig['celery_log_path'], group, queue+'_supervisor.log'),
               os.path.join(self.__projectsConfig['celery_log_path'], group, queue+'_supervisor_error.log'),
               int(self.__projectsConfig['supervisor_priority']),
               groupname,
               group + '_' + queue
               )
        self.__touchFile(supervisorFile, supervisor)
        logger.info('mk queue %s of %s group success' % (queue,group))

    def __touchFile(self, filename='', content=''):
        handler = open(filename, 'a+')
        handler.write('')
        handler.write(content)
        handler.flush()
        handler.close()
        return True
