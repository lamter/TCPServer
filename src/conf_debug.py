#coding=utf-8
'''
Created on 2015-10-24

@author: Shawn
'''

import logging
import datetime

import conf_server

# 服务器的IP地址
# conf_server.SERVER_IP = '127.0.0.1'
# conf_server.SERVER_PORT = 8912

# 加密
conf_server.AES_KEY = None

# 测试环境
conf_server.DEBUG = True
conf_server.LOG_LEVEL = logging.DEBUG
conf_server.PRODUCTION = True

