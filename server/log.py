#coding=utf-8
'''
Created on 2015-10-24

@author: Shawn
'''

from gevent import monkey
monkey.patch_all()

import sys
import os
import logging


import conf_server

if __name__ == "__main__":
    try:
        import conf_debug
    except:
        pass

# 获取日志实例 root
logger = logging.getLogger()

# 设置日志级别
logger.setLevel(conf_server.LOG_LEVEL)

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 设置日志句柄
hanlders = []
fh = None
if conf_server.PRODUCTION:
    # 生产环境，记录日志文件
    logFileName = os.path.join(conf_server.LOG_PATH, conf_server.SERVER_NAME+'.log')
    fh = logging.FileHandler(logFileName)           # 设置 记录文件名
    fh.setLevel(logging.INFO)                       # 设置记录级别  - info
    fh.setFormatter(formatter)
    logger.addHandler(fh)                           # 写入日志文件
    hanlders.append(fh)                             # 保存到句柄列表

ch = None
if conf_server.DEVELOPMENT:
    # 开发模式，输出到控制台
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)                      # 设置记录界别 - debug
    # ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == "__main__":
    logging.info('456')


