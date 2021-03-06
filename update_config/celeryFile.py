# _*_ coding:utf-8 _*_
from __future__ import absolute_import
import os
from CeleryDatabases.CeleryDatabases import CeleryDatabases
from clog.clog import logger
from celeryConfig import pconfig as pconfig

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
        cDatabase = CeleryDatabases()
        configDic = cDatabase.get_workerconfig()
        if configDic:
            for one in configDic:
                self.__projectsConfig[one.name] = one.value

    def checkConfig(self, group=None, queue=None, gid=0, queueid=0, supervisorGroupName=''):
        if(self. hasGroup(group)):
            self.deleteConfig(group=group, queue=queue)

        self.generalConfig(group, queue, gid, queueid, supervisorGroupName)

    def supervisorRestart(self):
        logger.warning(os.system('supervisorctl reread'))
        logger.warning(os.system('supervisorctl update'))

    def supervisorRestartGroup(self,supervisorGroupName):
        #@todo centos update group 不支持，ｕbuntu 可以
        logger.warning(os.system('supervisorctl update'))

    def hasGroup(self, group):
        if(os.path.exists(os.path.join(self.__projectsConfig['programs'],group))):
            return True
        else:
            return False

    def deleteConfig(self, group=None, queue=None):
        #delete programs file
        self.__celeryRemoveDir(os.path.join(self.__projectsConfig['programs'],group,queue))
        #delete log file
        self.__celeryRemoveDir(os.path.join(self.__projectsConfig['celery_log_path'],group,queue))
        #delete supervisor file
        supervisorFile = os.path.join(pconfig.supervisor_config_path, group+'_'+queue+'_worker.'+pconfig.super_file_suffix)
        if(os.path.exists(supervisorFile)):
            os.remove(supervisorFile)
        logger.warning('delete queue %s of %s group success' % (queue,group))

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

    def generalConfig(self, group=None, queue=None, gid=0, queueid=0, supervisorGroupName=''):
        cDatabase = CeleryDatabases()
        #查询队列详情
        queueObj = cDatabase.get_queue_by_status(qid=queueid, status=1, return_one=True)
        if queueObj is None:
            return False
        #组装路径
        groupPath = os.path.join(self.__projectsConfig['programs'],group)
        queuePath = os.path.join(self.__projectsConfig['programs'],group,queue)
        celeryConfigDir = os.path.join(self.__projectsConfig['programs'],group,queue,'celeryconfig')
        supervisorFile = os.path.join(pconfig.supervisor_config_path, group+'_'+queue+'_worker.'+pconfig.super_file_suffix)
        celeryLogPath = os.path.join(self.__projectsConfig['celery_log_path'],group,queue)
        if (not os.path.exists(queuePath)):
            os.makedirs(queuePath)
        if (not os.path.isdir(celeryConfigDir)):
            os.makedirs(celeryConfigDir)
        if (not os.path.isdir(celeryLogPath)):
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
task_time_limit = %s
task_soft_time_limit = %s
worker_max_tasks_per_child = %s
worker_max_memory_per_child = %s
task_acks_late = True
task_reject_on_worker_lost = True   # Warning Enabling this can cause message loops; make sure you know what you're doing
worker_prefetch_multiplier = 0
worker_pool_restarts = True
task_ignore_result = False
task_store_errors_even_if_ignored = True
worker_enable_remote_control=True
worker_state_db=''
timezone='Asia/Shanghai'
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
       int(queueObj.timeout)+5,
       queueObj.timeout,
       queueObj.tasks_number,
       queueObj.memory
       # os.path.join(self.__projectsConfig['celery_log_path'],group,queue,queue)
       )
        self.__touchFile(os.path.join(celeryConfigDir,'celeryconfig.py'),celeryConfigFile)

        # touch celery.py
        celeryFile = """# _*_ coding:utf-8 _*_
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
import traceback
import hashlib
import os
import base64

from celery.exceptions import Reject
from %s.celery import app
from CeleryCustomTask.CeleryCustomTask import Ctask
from clog.clog import logger

@app.task(
          base=Ctask,
          bind=True,
          )
def handler(self, payload):
    try:
        obj = json.loads(payload)
        # callback | command
        dispatch = obj['c']
        # payload
        payload = obj['p']
        # message type
        type = obj['t']
        # exec command
        if type == '2':
            return os.system('%%s %%s' %% (dispatch, payload))
        # exec url callback
        elif type == '1':
            r= requests.post(dispatch,{'payload':payload})
            r.raise_for_status()
            data = {'queuename':'%s', 'payload':payload, 'result':r.text}
            return json.dumps(data)
        
    except MemoryError as exc:
        raise Reject(exc, requeue=True)
    except OSError as exc:
        if exc.errno == errno.ENOMEM:
            raise Reject(exc, requeue=True)
    except Exception as exc:
        logger.error('Task failure, payload is %s', (payload), format(exc), traceback.format_exc())
        self.retry(countdown=3, exc=exc, max_retries=3)

def genearteMD5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()
""" % (queue,group+'_'+queue, '%s, mes:%s, trace:%s')
        self.__touchFile(os.path.join(queuePath, 'task.py'), taskFile)

        # init.sh file
        initfile = """#!/bin/bash
source %s
celery --app=%s worker -l %s -Ofair -n $1 -Q %s -c %d -f %s
""" % (os.path.join(pconfig.venvpath,'bin/activate'),
       queue,
       pconfig.log_level,
       group+'_'+queue,
       queueObj.concurrency,
       os.path.join(self.__projectsConfig['celery_log_path'],group,queue+'_worker_out.log'),)
        self.__touchFile(os.path.join(queuePath, 'init.sh'), initfile)

        # touch supervisor file
        # command = bash % s"%s_%%h_%%(process_num)d"
        supervisor = """[program:%s]
command=bash %s %s_%%%%h_%%(process_num)d
directory=%s
user=%s
numprocs=%d
process_name=%%(program_name)s_%%(process_num)d@%%(host_node_name)s
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
       os.path.join(queuePath, 'init.sh'),
       group+'_'+queue,
       os.path.join(self.__projectsConfig['programs'], group),
       queueObj.executor,
       int(self.__projectsConfig['numprocs']),
       os.path.join(self.__projectsConfig['celery_log_path'], group, queue+'_supervisor.log'),
       os.path.join(self.__projectsConfig['celery_log_path'], group, queue+'_supervisor_error.log'),
       int(self.__projectsConfig['supervisor_priority']),
       supervisorGroupName,
       group + '_' + queue
       )
        self.__touchFile(supervisorFile, supervisor)
        logger.warning('mk queue %s of %s group success' % (queue,group))

    def __touchFile(self, filename='', content=''):
        handler = open(filename, 'a+')
        handler.write('')
        handler.write(content)
        handler.flush()
        handler.close()
        return True
