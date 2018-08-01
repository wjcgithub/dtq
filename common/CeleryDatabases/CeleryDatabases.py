# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pymysql
from celeryConfig import mysqlconfig as config
from clog.clog import logger

class CeleryDatabases(object):

    def getConnect(self):
        conn = pymysql.connect(config.db_host, config.db_user, config.db_pass,config.db_name,
                                      use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
        return conn


    def execute_query(self, query, args=(), return_one=False, exec_many=False):
        conn = self.getConnect()
        try:
            with conn.cursor() as cursor:
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
            conn.close()
            del conn
        return cursor.fetchone() if return_one else cursor.fetchall()
