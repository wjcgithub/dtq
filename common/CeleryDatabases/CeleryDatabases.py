# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pymysql
from celeryConfig import mysqlconfig as config
import warnings
import logging

warnings.filterwarnings('error', category=pymysql.err.Warning)
# use logging module for easy debug
logging.basicConfig(format='%(asctime)s %(levelname)8s: %(message)s', datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel('WARNING')

class CeleryDatabases(object):
    __conn = None

    def __init__(self):
        self.__conn = None

    def getConnect(self):
        self.__conn = pymysql.connect(config.db_host, config.db_user, config.db_pass,config.db_name,
                                      use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)

        return self.__conn


    def execute_query(self, query, args=(), return_one=False, exec_many=False):
        self.getConnect()
        sql = 'select * from queues where id = %s' % (id)
        try:
            with self.__conn.cursor() as cursor:
                cursor.execute('SET NAMES utf8;')
                cursor.execute('SET CHARACTER SET utf8;')
                cursor.execute('SET character_set_connection=utf8;')
                if exec_many:
                    cursor.executemany(query, args)
                else:
                    cursor.execute(query, args)
        except Exception as e:
            logger.error('查询数据错误:%s' % (query))
        finally:
            self.__conn.close()
        return cursor.fetchone() if return_one else cursor.fetchall()
