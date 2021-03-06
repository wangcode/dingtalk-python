#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午4:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : extensions.py
# @Software: PyCharm
import logging
from dingtalk import DingTalkApp
from config import current_config
from dingtalk import SessionManager

__author__ = 'blackmatrix'

"""
这里为了测试方便，引入了之前编写的config模块，本身SDK的使用不需要此模块。
类似current_config.DING_CORP_ID的操作，本质上是从配置文件中读取配置项的值。
实际的项目运用中，可以通过其他方式获取配置参数。
"""

CORP_ID = current_config.DING_CORP_ID
CORP_SECRET = current_config.DING_CORP_SECRET
AGENT_ID = current_config.DING_AGENT_ID
DOMAIN = current_config.DING_DOMAIN
AES_KEY = current_config.DING_AES_KEY
CALLBACK_URL = current_config.DING_CALLBACK
DING_SESSION_HOST = current_config.DING_SESSION_HOST
DING_SESSION_PORT = current_config.DING_SESSION_PORT
DING_SESSION_USER = current_config.DING_SESSION_USER
DING_SESSION_PASS = current_config.DING_SESSION_PASS
DING_SESSION_DB = current_config.DING_SESSION_DB


class MySQLSessionManager(SessionManager):

    """
    一个简单实现的使用MySQL实现管理access token和jsapi ticket过期时间的例子

    SET NAMES utf8mb4;
    SET FOREIGN_KEY_CHECKS = 0;
    -- ----------------------------
    -- Table structure for dingtalk_cache
    -- ----------------------------
    DROP TABLE IF EXISTS `dingtalk_cache`;
    CREATE TABLE `dingtalk_cache` (
      `key` varchar(255) NOT NULL,
      `value` varchar(255) NOT NULL,
      `create_time` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
      `expire_time` datetime NOT NULL,
      PRIMARY KEY (`key`),
      KEY `row_id` (`key`,`value`,`create_time`,`expire_time`) USING BTREE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    SET FOREIGN_KEY_CHECKS = 1;
    """

    def __init__(self, host, user, pass_, db, port=3306):
        import pymysql
        self.connection = pymysql.connect(host=host, port=port, user=user, password=pass_, db=db)
        self.connection.autocommit(True)

    def set(self, key, value, expires):
        cursor = self.connection.cursor()
        from datetime import datetime, timedelta
        create_time = datetime.now()
        expire_time = create_time + timedelta(seconds=expires)
        select_sql = 'SELECT sql_no_cache `key`, `value`, expire_time FROM dingtalk_cache WHERE `key`="{}"'.format(key)
        self.check_connect()
        data = cursor.execute(select_sql)
        # 因为数据库是varchar类型
        value = str(value)
        if data < 1:
            sql = 'INSERT INTO dingtalk_cache(`key`,`value`,create_time,expire_time) VALUES("{}","{}","{}","{}")'.format(
                key, value, create_time.strftime('%Y-%m-%d %H:%M:%S'), expire_time.strftime('%Y-%m-%d %H:%M:%S'))

        else:
            sql = 'UPDATE dingtalk_cache SET `value`="{}", create_time="{}", expire_time="{}" WHERE `key`="{}"'.format(
                value, create_time, expire_time, key)
        self.check_connect()
        cursor.execute(sql)
        cursor.close()

    def get(self, key):
        try:
            cursor = self.connection.cursor()
            from datetime import datetime
            select_sql = 'SELECT sql_no_cache `key`, `value`, expire_time FROM dingtalk_cache WHERE `key`="{}"'.format(key)
            self.check_connect()
            cursor.execute(select_sql)
            row = cursor.fetchone()
            key, value, expire_time = row
            now = datetime.now()
            if now >= expire_time:
                return None
            else:
                return value
        except TypeError:
            return None
        except Exception as ex:
            logging.error(ex)
            return None

    def delete(self, key):
        del_sql = 'DELETE FROM dingtalk_cache WHERE `key`="{}"'.format(key)
        cursor = self.connection.cursor()
        self.check_connect()
        cursor.execute(del_sql)
        cursor.close()

    def check_connect(self):
        try:
            self.connection.ping()
        except BaseException as ex:
            logging.error(ex)
            self.connection()

# 钉钉会话管理，Mysql支持
session_manager = MySQLSessionManager(host=DING_SESSION_HOST, port=DING_SESSION_PORT,
                                      user=DING_SESSION_USER, pass_=DING_SESSION_PASS,
                                      db=DING_SESSION_DB)

# 钉钉会话管理，Memcached支持
# from memcache import Client
# session_manager = Client(current_config.CACHE_MEMCACHED_SERVERS)

# 钉钉会话管理，Redis支持
# import redis
# session_manager = redis.Redis(host=current_config.CACHE_REDIS_SERVERS,
#                               port=current_config.CACHE_REDIS_PORT,
#                               db=current_config.CACHE_REDIS_DB)

# 这里选择从配置文件读取设定的缓存对象
# session_manager = current_config.DING_SESSION_MANAGER

# 实例化一个钉钉的对象
dd_config = {'corp_id': CORP_ID, 'corp_secret': CORP_SECRET, 'agent_id': AGENT_ID,
             'domain': DOMAIN, 'aes_key': AES_KEY, 'callback_url': CALLBACK_URL}
# redis、memcached或自定义缓存对象，三者选一个传入给DingTalkApp的session_manager属性即可
app = DingTalkApp(name='test', session_manager=session_manager, **dd_config)
