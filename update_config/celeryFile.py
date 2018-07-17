#!/usr/bin/env python3.5
# _*_ coding:utf-8 _*_
from __future__ import absolute_import
import os

from common.celeryConfig import projects
from common.CeleryDatabases.CeleryDatabases import CeleryDatabases
from common.clog.clog import logger

class CeleryConfigFile(object):
    __projectsConfig = None
    __rootPath = ''
    __programsPath = ''
    __supervisorConfPath = ''

    def __init__(self):
        self.__projectsConfig = projects
        self.__rootPath = projects.rootPath
        self.__programsPath = os.path.join(self.__rootPath,'programs')
        self.__supervisorConfPath = '/etc/supervisor/conf.d/'

    def checkConfig(self, group=None, queue=None, gid=0, queueid=0, groupname=''):
        if(self. hasGroup(group)):
            self.__deleteConfig(group=group, queue=queue)

        self.__generalConfig(group, queue, gid, queueid, groupname)
        self.__supervisorRestart()

    def __supervisorRestart(self):
        logger.info(os.system('supervisorctl reread'))
        logger.info(os.system('supervisorctl update'))

    def supervisorRestartGroup(self):
        logger.info(os.system('supervisorctl restart xin_celery'))

    def hasGroup(self, group):
        if(os.path.exists(os.path.join(self.__programsPath,group))):
            return True
        else:
            return False

    def __deleteConfig(self, group=None, queue=None):
        self.__celeryRemoveDir(os.path.join(self.__programsPath,group,queue))
        self.__celeryRemoveDir(os.path.join(self.__rootPath,'log',group,queue))
        supervisorFile = os.path.join(self.__supervisorConfPath, group+'_'+queue+'_worker.conf')
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
        groupPath = os.path.join(self.__programsPath,group)
        queuePath = os.path.join(self.__programsPath,group,queue)
        celeryConfigDir = os.path.join(self.__programsPath,group,queue,'celeryconfig')
        supervisorFile = os.path.join('/etc/supervisor/conf.d/', group+'_'+queue+'_worker.conf')
        celeryLogPath = os.path.join(self.__rootPath,'log',group,queue)
        os.makedirs(queuePath)
        os.makedirs(celeryConfigDir)
        os.makedirs(celeryLogPath)
        os.system('setfacl -m u:celery:rwx '+self.__rootPath)
        os.system('setfacl -d -m u:celery:rwx '+self.__rootPath)
        os.system('setfacl -R -m u:celery:rwx '+self.__rootPath)
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
""" % (self.__projectsConfig.broker_url+self.__projectsConfig.exchange,
       self.__projectsConfig.result_backend,
       queue,
       group+'_'+queue,
       self.__projectsConfig.exchange,
       group+'_'+queue,
       queue,
       group+'_'+queue,
       self.__projectsConfig.exchange,
       group + '_' + queue,
       os.path.join(self.__rootPath,'log/',group,queue,queue)
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
    except MemoryError as exc:
        raise Reject(exc, requeue=True)
    except OSError as exc:
        if exc.errno == errno.ENOMEM:
            raise Reject(exc, requeue=True)
    except Exception as exc:
        self.retry(countdown=3, exc=exc, max_retries=3)
        """ % (queue, queueDic['callback_url'],queueDic['timeout'])
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
priority=999

[group:%s]
programs=%s
        """ % (group+'_'+queue,
               queue,
               group+'_'+queue,
               group+'_'+queue,
               queueDic['concurrency'],
               os.path.join(self.__rootPath,'log',group,queue+'_worker.log'),
               os.path.join(self.__programsPath, group),
               self.__projectsConfig.numprocs,
               os.path.join(self.__rootPath, 'log', group, queue+'_supervisor.log'),
               os.path.join(self.__rootPath, 'log', group, queue+'_supervisor_error.log'),
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

    def hasQueue(self, queue):
        pass