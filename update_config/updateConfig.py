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
from .celeryFile import CeleryConfigFile
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
        """删除队列"""
        queue = self.__cDatabase.get_queue_by_status(qid=int(queueid), return_one=True)
        if queue is not None:
            group = self.__cDatabase.get_group_by_status(gid=int(queue.gid), status=1, return_one=True)
            if group is not None:
                groupName = self.__generateGroupName(group.id)
                queueName = queue.name
                cc = CeleryConfigFile()
                if(cc.hasGroup(groupName)):
                    cc.deleteConfig(group=groupName, queue=queueName)
                    cc.supervisorRestart()
                    logger.warning('delete queue %s of %s group success' % (queueName, groupName))

    def __performUpdate(self, queueid):
        """处理队列更新"""
        queue = self.__cDatabase.get_queue_by_status(qid=int(queueid), status=1, return_one=True)
        if queue is not None:
            group = self.__cDatabase.get_group_by_status(gid=int(queue.gid), status=1, return_one=True)
            if group is not None:
                groupName = self.__generateGroupName(group.id)
                queueName = queue.name
                cc = CeleryConfigFile()
                cc.checkConfig(groupName,queueName,queue['gid'], queueid, '')
                cc.supervisorRestart()
                logger.warning('update queue %s of %s group success' % (queueName, groupName))

    def __restartAllQueue(self):
        """重启所有队列"""
        cc = CeleryConfigFile()
        groups = self.__cDatabase.get_group_by_status(status=1,return_one=False)
        supervisorGroupName = 'xin_celery'
        if groups:
            for group in groups:
                queues = self.__cDatabase.get_queue_by_status(gid=group.id, status=1, return_one=False)
                if queues:
                    for queue in queues:
                        cc.checkConfig(self.__generateGroupName(group.id), queue.name, group.id, queue.id, supervisorGroupName)
            cc.supervisorRestartGroup(supervisorGroupName)

    def __generateGroupName(self,oldname):
        return 'group'+str(oldname)