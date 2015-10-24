#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''

import datetime

# 服务器的IP地址
SERVER_IP = '127.0.0.1'
# SERVER_PORT = 8912
SERVER_PORT = 8912

# socket 链接缓存大小
SOCKET_CACHE_SIZE = 100
SOCKET_CACHE_TIME_OUT = datetime.timedelta(seconds=100)  # 十秒没有建立实例就是超时

# 并发数量
ASYNC_SIZE = 1000

# 保持的 socket 链接数
SOCKET_SIZE = 1000

# AES_KEY 要16位字符
AES_KEY = '0123456789ABCDEF'

