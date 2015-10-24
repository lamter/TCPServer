#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''

import datetime
import functools
import traceback

import conf_server
from lib.woodmoo import loadInt32

from gevent import sleep
from gevent.socket import socket as gsocket
from gevent.server import StreamServer
from gevent.pool import Pool
from gevent.queue import Queue

from serverdata import ServerData
from innerrequest import InnerRequest


def forever(func):
    # 被永久执行的并发的修饰器, 旗下的函数不再需要 while 1 的永久循环
    @functools.wraps(func)
    def wrapper(*args, **kw):
        # print 'call %s():' % func.__name__
        try:
            while 1:
                r =  func(*args, **kw)
        except:
            traceback.print_exc()

        return r
    return wrapper


class Server(StreamServer):
    """
    socket 服务器
    """
    def __init__(self, address, async=False):
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


    def connection_handler(self, socket, address):
        """
        socket 建立链接的时候进入
        :param socket:
        :param address:
        :return:
        """
        print('new connection from %s:%s' % address)

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

            except:
                traceback.print_exc()
                # 并发执行这个请求
                # self.spawn(InnerRequest.new(_json, socket).doIt)
            finally:
                self.sockets.put(socket)

        # 走完一轮， 跳转
        sleep(0)



    @forever
    def async(self):
        """
        :return:
        """
        print(u' sync, 未完成')


    def get_AES_KEY(self):
        """

        :return:
        """
        return conf_server.AES_KEY



def run():
    # 服务器实例
    address = (conf_server.SERVER_IP, conf_server.SERVER_PORT)
    server = Server(address)
    server.serve_forever()


if __name__ == "__main__":
    # you can add conf_debug.py to set arg of conf_server.
    import conf_debug
    run()

