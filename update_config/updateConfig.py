# _*_ coding:utf-8 _*_
from __future__ import absolute_import, unicode_literals
import time
import redis
import sys
import os
sys.path.append(os.path.abspath('.')+'/common')
from celeryConfig import redisconfig
from celeryConfig import pconfig
from CeleryDatabases.CeleryDatabases import CeleryDatabases
from update_config.celeryFile import CeleryConfigFile
from clog.clog import logger


class UpdateConfig():
    __pool = None
    __redis = None
    __cDatabase = None
    __changeKey = ''
    __restartAllQueueFlag = ''

    def __init__(self):
        self.__redisPool()
        self.__changeKey = 'celery:changelist:'+pconfig.hostname
        self.__deleteKey = 'celery:deletelist:'+pconfig.hostname
        self.__restartAllQueueFlag = 'celery:restartallqueue:'+pconfig.hostname
        self.__cDatabase = CeleryDatabases()

    def start(self):
        self.__getRedis()
        # 处理新加和更新的任务，　一律为add任务，　先删除后添加
        while(True):
            try:
                #移除队列
                members = self.__redis.smembers(self.__deleteKey)
                for queueid in members:
                    self.__deleteQueue(queueid.decode())
                    self.__redis.srem(self.__deleteKey, queueid.decode())

                # 处理变更的队列
                members = self.__redis.smembers(self.__changeKey)
                for queueid in members:
                    self.__performUpdate(queueid.decode())
                    self.__redis.srem(self.__changeKey,queueid.decode())

                # 重启所有队列
                restart = self.__redis.get(self.__restartAllQueueFlag)

                if restart:
                    if (restart.decode('utf-8')=='1'):
                        self.__redis.set(self.__restartAllQueueFlag,0)
                        self.__restartAllQueue()
                        logger.info('重启所有服务')
                time.sleep(2)
            except Exception as e:
                logger.error(e, exc_info=True)

    def __redisPool(self):
        self.__pool = redis.ConnectionPool(host=redisconfig.host, port=redisconfig.port, db=redisconfig.db)

    def __getRedis(self):
        self.__redis = redis.Redis(connection_pool=self.__pool)

    def __deleteQueue(self, queueid):
        queue = ''
        group = ''
        queue = self.getQueueById(queueid)
        if queue is not None:
            group = self.getGroupById(queue['gid'])
            groupName = group['name']
            queueName = queue['name']
            cc = CeleryConfigFile()
            if(cc.hasGroup(groupName)):
                cc.deleteConfig(groupName,queueName)
                cc.supervisorRestart()
                logger.warning('delete queue %s of %s group success' % (queueName, groupName))

    def __performUpdate(self, queueid):
        queue = ''
        group = ''
        queue = self.getQueueById(queueid)
        if queue is not None:
            group = self.getGroupById(queue['gid'])
            groupName = group['name']
            queueName = queue['name']
            cc = CeleryConfigFile()
            cc.checkConfig(groupName,queueName,queue['gid'], queueid, '')
            cc.supervisorRestart()

    def getGroupById(self, gid):
        result = None
        sql = 'select * from groups where id = %s' % (gid)
        result = self.__cDatabase.execute_query(sql, return_one=True)
        return result


    def getQueueById(self, id):
        result = None
        sql = 'select * from queues where id = %s' % (id)
        result = self.__cDatabase.execute_query(sql,return_one=True)
        return result

    #重启所有队列
    def __restartAllQueue(self):
        cc = CeleryConfigFile()
        sql = 'select id,name from groups where status=1'
        groups = self.__cDatabase.execute_query(sql, return_one=False)
        # groupname = 'xin_celery_'+str(time.time())
        groupname = 'xin_celery'
        if groups:
            for group in groups:
                sql = 'select id,name from queues where gid = %s and status=1' % (group['id'])
                queues = self.__cDatabase.execute_query(sql, return_one=False)
                if queues:
                    for queue in queues:
                        cc.checkConfig(group['name'], queue['name'], group['id'], queue['id'], groupname)
            cc.supervisorRestartGroup(groupname)

