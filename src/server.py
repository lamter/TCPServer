#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''

from gevent import monkey
monkey.patch_all()

import datetime
import functools
import traceback
import signal
import logging

from lib.woodmoo import loadInt32

import gevent
from gevent import sleep
from gevent.server import StreamServer
from gevent.pool import Pool
from gevent.queue import Queue

import conf_server
if __name__ == "__main__": import conf_debug
import log
from serverdata import ServerData
from innerrequest import InnerRequest



SHUT_DOWN_SIGN = [
    signal.SIGQUIT,     # kill 信号
    signal.SIGINT,      # 键盘信号
]


def forever(func):
    # 被永久执行的并发的修饰器, 旗下的函数不再需要 while 1 的永久循环
    @functools.wraps(func)
    def wrapper(*args, **kw):
        # print 'call %s():' % func.__name__
        try:
            while 1:
                r = func(*args, **kw)
                sleep(0)    # 完成之后跳转
        except gevent.GreenletExit:
            logging.info('stop forever %s ...' % func.__name__)

        return r
    return wrapper



class Server(StreamServer):
    """
    socket 服务器
    """
    def __init__(self, address, async=False):
        for sign in SHUT_DOWN_SIGN:
            ''' 关服信号 '''
            gevent.signal(sign, self.shutdown)

        pool = Pool(conf_server.ASYNC_SIZE)
        StreamServer.__init__(self, address, self.connection_handler, spawn=pool)

        self.serverData = ServerData(self)

        self.sockets = Queue(conf_server.SOCKET_SIZE)                    # 绑定了服务器实例的 socket

        if async:
            # 异步处理每个 socket 的数据
            self.spawn(self.async)
        else:
            # 顺序逐个处理 socket 的数据,返回后再处理下一个
            self.spawn(self.sync)

        # 循环记录日志
        # self.spawn(self.flushLog)


    def connection_handler(self, socket, address):
        """
        socket 建立链接的时候进入
        :param socket:
        :param address:
        :return:
        """
        logging.info('new connection from %s:%s' % address)

        # 缓存链接
        self.saveSocket(socket)

        # 设置缓存超时，如果 socket 缓存一直没有绑定到本地实例，移动到 sockets, 那么将会被断掉
        self.setSocketCacheTimeOut(socket)

        # print self.socketsCache.qsize()



    def setSocketCacheTimeOut(self, socket):
        """
        给socket 缓存设置超时时间
        :return:
        """
        socket.cacheTimeOut = datetime.datetime.now() + conf_server.SOCKET_CACHE_TIME_OUT


    def saveSocket(self, socket):
        """
        :param socket:
        :return:
        """

        self.sockets.put(socket)


    def spawn(self, func, *args, **kwargs):
        """
        并发任务
        :return:
        """
        return self.pool.spawn(func, *args, **kwargs)


    @forever
    def sync(self):
        """
        异步处理接受到的 socket 数据，执行请求逻辑，并响应
        :return:
        """
        now = datetime.datetime.now()
        for _ in xrange(self.sockets.qsize()):
            try:
                socket = self.sockets.get()
                if socket.cacheTimeOut is not None and socket.cacheTimeOut <= now:
                    # 过期的 socket 关闭并抛弃
                    socket.close()
                    continue

                # 采用Int32位，解密解压出数据，可根据需求更改
                AES_KEY = self.get_AES_KEY()
                _json = loadInt32(AES_KEY, socket)

            except gevent.GreenletExit:
                raise
            except:
                logging.error(traceback.format_exc())
            finally:
                self.sockets.put(socket)


    @forever
    def async(self):
        """
        :return:
        """
        logging.warn('Server.async 未完成')


    def get_AES_KEY(self):
        """

        :return:
        """
        return conf_server.AES_KEY


    def shutdown(self):
        """
        关服时要做的事情
        :return:
        """

        # 关闭日志模块
        logging.shutdown()

        # 关闭服务器
        self.close()


def run():
    # 服务器实例
    address = (conf_server.SERVER_IP, conf_server.SERVER_PORT)
    server = Server(address)
    logging.info('start server ...')
    server.serve_forever()


if __name__ == "__main__":
    run()

