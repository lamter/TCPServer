#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''

import datetime
import logging

# 服务器的IP地址
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8912
SERVER_NAME = 'tcpserver'

# 运行环境
PRODUCTION = False              # 生产环境
DEVELOPMENT = True              # 开发环境
DEBUG = False                   # 测试环境

# socket 链接缓存大小
SOCKET_CACHE_SIZE = 100
SOCKET_CACHE_TIME_OUT = datetime.timedelta(seconds=100)  # 十秒没有建立实例就是超时
SOCKET_SEND_TIME_OUT = datetime.timedelta(seconds=10)      # n 秒发送数据超时

# socket 超时重发次数
SOCKET_TIME_OUT_RESEND_TIMES = 3

# 并发数量
ASYNC_SIZE = 1000

# 保持的 socket 链接数
SOCKET_SIZE = 1000

# AES_KEY 要16位字符
AES_KEY = '0123456789ABCDEF'


# 日志相关
LOG_LEVEL = logging.INFO
LOG_PATH = 'log/'