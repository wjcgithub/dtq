#!/usr/bin/env python
# coding=utf-8
from DBUtils.PooledDB import PooledDB
import MySQLdb as mysql
from utils import util
import traceback
import config
import sys


class DB():
    def __init__(self):
        self.host = config.db_host
        self.name = config.db_name
        self.user = config.db_user
        self.passwd = config.db_passwd
        self.pool = PooledDB(mysql, mincached=4, maxcached=10, host=self.host, db=self.name, user=self.user,
                             passwd=self.passwd, setsession=['SET AUTOCOMMIT = 1'])

    # 连接数据库
    def connect_db(self):
        self.db = self.pool.connection()
        self.cur = self.db.cursor()

    # 关闭连接
    def close_db(self):
        self.cur.close()
        self.db.close()

    # 执行sql
    def execute(self, sql):
        self.connect_db()
        return self.cur.execute(sql)

    # 获取所有数据列表
    def get_list(self, table, fields):
        sql = "select %s from %s" % (",".join(fields), table)
        try:
            self.execute(sql)
            result = self.cur.fetchall()
            if result:
                result = [dict((k, row[i]) for i, k in enumerate(fields)) for row in result]
            else:
                result = {}
            return result;
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()

    # 获取某一条数据，返回字典
    def get_one(self, table, fields, where):
        if isinstance(where, dict) and where:
            conditions = []
            for k, v in where.items():
                conditions.append("%s='%s'" % (k, v))
        sql = "select %s from %s where %s" % (",".join(fields), table, ' AND '.join(conditions))
        try:
            self.execute(sql)
            result = self.cur.fetchone()
            if result:
                result = dict((k, result[i]) for i, k in enumerate(fields))
            else:
                result = {}
            return result
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()

    # 更新数据
    def update(self, table, fields):
        data = ",".join(["%s='%s'" % (k, v) for k, v in fields.items()])
        sql = "update %s set %s where id=%s " % (table, data, fields["id"])
        try:
            return self.execute(sql)
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()

    # 添加数据
    def create(self, table, data):
        fields, values = [], []
        for k, v in data.items():
            fields.append(k)
            values.append("'%s'" % v)
        sql = "insert into %s (%s) values (%s)" % (table, ",".join(fields), ",".join(values))
        try:
            return self.execute(sql)
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()

    # 删除数据
    def delete(self, table, where):
        if isinstance(where, dict) and where:
            conditions = []
            for k, v in where.items():
                conditions.append("%s='%s'" % (k, v))
        sql = "delete from %s where %s" % (table, ' AND '.join(conditions))
        try:
            return self.execute(sql)
        except:
            util.WriteLog('db').info("Execute '%s' error: %s" % (sql, traceback.format_exc()))
        finally:
            self.close_db()