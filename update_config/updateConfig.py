# _*_ coding:utf-8 _*_
from __future__ import absolute_import, unicode_literals
import time
import redis
import sys
import os
sys.path.append(os.path.abspath('.')+'/common')
from celeryConfig import redisconfig
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
        self.__changeKey = 'celery:changelist'
        self.__restartAllQueueFlag = 'celery:restartallqueue'
        self.__cDatabase = CeleryDatabases()

    def start(self):
        self.__getRedis()
        # 处理新加和更新的任务，　一律为add任务，　先删除后添加
        while(True):
            try:
                # 处理变更的队列
                members = self.__redis.smembers(self.__changeKey)
                for queueid in members:
                    self.__performUpdate(queueid.decode())
                    self.__redis.srem(self.__changeKey,queueid.decode())

                # 重启所有队列
                restart = self.__redis.get(self.__restartAllQueueFlag)
                if (restart.decode('utf-8')=='1'):
                    self.__redis.set(self.__restartAllQueueFlag,0)
                    self.__restartAllQueue()
                    logger.info('重启所有服务')
                time.sleep(1)
            except Exception as e:
                logger.error(e, exc_info=True)

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
        sql = 'select id,name from groups'
        groups = self.__cDatabase.execute_query(sql, return_one=False)
        groupname = 'xin_celery_'+str(time.time())
        groupname = 'xin_celery'
        if groups:
            for group in groups:
                logger.info(group['name'])
                sql = 'select id,name from queues where gid = %s' % (group['id'])
                queues = self.__cDatabase.execute_query(sql, return_one=False)
                if queues:
                    for queue in queues:
                        logger.info(group['name'])
                        logger.info(queue['name'])
                        logger.info(group['id'])
                        logger.info(queue['id'])
                        logger.info('===============')
                        cc.checkConfig(group['name'], queue['name'], group['id'], queue['id'], groupname)

            cc.supervisorRestartGroup(groupname)

