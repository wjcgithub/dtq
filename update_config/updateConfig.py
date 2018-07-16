#!/usr/bin/env python3.5
# _*_ coding:utf-8 _*_
from __future__ import absolute_import, unicode_literals
import time
import redis
import sys
import os
# sys.path.append(os.path.abspath('.')+'/common')
from common.celeryConfig import redisconfig
from common.CeleryDatabases.CeleryDatabases import CeleryDatabases
from update_config.celeryFile import CeleryConfigFile

class UpdateConfig():
    __pool = None
    __redis = None
    __cDatabase = None
    __changeKey = ''

    def __init__(self):
        self.__redisPool()
        self.__changeKey = 'celery:changelist'
        self.__cDatabase = CeleryDatabases()

    def start(self):
        self.__getRedis()
        # 处理新加和更新的任务，　一律为add任务，　先删除后添加
        while(True):
            members = self.__redis.smembers(self.__changeKey)
            for queueid in members:
                self.__performUpdate(queueid.decode())
                self.__redis.srem(self.__changeKey,queueid.decode())
            time.sleep(1)

    def __redisPool(self):
        self.__pool = redis.ConnectionPool(host=redisconfig.host, port=redisconfig.port, db=redisconfig.db)

    def __getRedis(self):
        self.__redis = redis.Redis(connection_pool=self.__pool)

    def __performUpdate(self, queueid):
        queue = None
        group = None
        queue = self.getQueueById(queueid)
        if queue is not None:
            group = self.getGroupById(queue['gid'])
            groupName = group['name']
            queueName = queue['name']
            self.__performConfig(groupName,queueName,queue['gid'], queueid)

    def getChange(self):
        pass

    def getGroupById(self, gid):
        result = None
        sql = 'select * from groups where id = %s' % (gid)
        result = self.__cDatabase.execute_query(sql, return_one=True)
        return result

    def getQueueByGroup(self):
        pass

    def getQueueById(self, id):
        result = None
        sql = 'select * from queues where id = %s' % (id)
        result = self.__cDatabase.execute_query(sql,return_one=True)
        return result

    def __performConfig(self, group=None, queue=None, gid=0, queueid=0):
        cc = CeleryConfigFile()
        cc.checkConfig(group, queue, gid, queueid)

    def updateSupervisorConfig(self):
        pass

    def restartSupervisor(self):
        pass