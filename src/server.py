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

from lib.woodmoo import *

import gevent
from gevent import sleep
from gevent.server import StreamServer
from gevent.pool import Pool
from gevent.queue import Queue

import conf_server
if __name__ == "__main__":
    import conf_debug

import log
from serverdata import ServerData
from request import BaseRequest



SHUT_DOWN_SIGN = [
    signal.SIGQUIT,     # kill 信号
    signal.SIGINT,      # 键盘信号
]


def forever(func):
    # 被永久执行的并发的修饰器, 旗下的函数不再需要 while 1 的永久循环
    @functools.wraps(func)
    def wrapper(*args, **kw):
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

        ''' 所有 socket 放在这里用于轮询 '''
        self.sockets = Queue(conf_server.SOCKET_SIZE)                    # 绑定了服务器实例的 socket

        # 处理收到的数据
        self.spawn(self.receive)

        # if async:
        #     # 异步处理每个 socket 的数据
        #     self.spawn(self.async)
        # else:
        #     # 顺序逐个处理 socket 的数据,返回后再处理下一个
        #     self.spawn(self.sync)

        # 循环记录日志
        # self.spawn(self.flushLog)


    def connection_handler(self, _socket, address):
        """
        socket 建立链接的时候进入
        :param socket:
        :param address:
        :return:
        """

        logging.info('new connection from %s:%s' % address)
        # 绑定其地址端口
        _socket.host, _socket.port = address

        # 缓存链接
        self.saveSocket(_socket)

        # 设置缓存超时，如果 socket 缓存一直没有绑定到本地实例，移动到 sockets, 那么将会被断掉
        self.setSocketTimeOut(_socket)



    def setSocketTimeOut(self, _socket):
        """
        给socket 设置超时时间
        :return:
        """
        # 缓存超时
        _socket.cacheTimeOut = datetime.datetime.now() + conf_server.SOCKET_CACHE_TIME_OUT

        # socket 本身的超时, n 秒后超时
        timeOutSeconds = conf_server.SOCKET_CACHE_TIME_OUT.total_seconds()
        _socket.settimeout(timeOutSeconds)


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
    def receive(self):
        """
        异步处理接受到的 socket 数据，执行请求逻辑，并响应
        :return:
        """
        now = datetime.datetime.now()
        for _ in xrange(self.sockets.qsize()):
            try:
                _socket = self.sockets.get()
                if not self.isSocketValid(_socket, now):
                    # 检查链接是否有效
                    continue

                # 采用Int32位，解密解压出数据，可根据需求更改
                AES_KEY = self.get_AES_KEY()
                data = loadInt32(_socket, AES_KEY)

                logging.debug(u'receive from %s:%s \n%s' % (_socket.host,_socket.port, data))

                # 业务逻辑处理，此处可重构
                if data:
                    self.async(data, _socket)

            except gevent.GreenletExit:
                raise
            except:
                logging.error(traceback.format_exc())
            finally:
                self.sockets.put(_socket)


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


    def async(self, _json, _socket):
        """
        异步模式的业务处理，并发业务
        :param _json: 传入的数据需要为 json 格式
        :param _socket:
        :return:
        """

        # 实例化 request
        r = BaseRequest.new(_json, _socket)
        # 执行逻辑
        r.doIt()


    def sendResponse(self, _response):
        """
        一个请求要发送数据
        :param response:
        :return:
        """
        # 在 async() 中绑定了 socket 链接
        _socket = _response.socket

        # json 格式的数据
        _json = _response.json()

        # 加压加密
        data = dumpInt32(_json, conf_server.AES_KEY)
        # logging.debug('send dat to %s:%s dat:\n' % (_socket.host, _socket.port) + data)

        def _send(_socket, data):

            try:
                _socket.sendall(data)
            except:
                err = 'Send dat to %s:%s faild. data len:%s err:\n' % (_socket.host, _socket.port, len(data))
                err += traceback.format_exc()
                logging.error(err)
                # 出错后断开这条 socket
                _socket.close()

        # 并发这条发送
        self.spawn(_send, _socket, data)


    def isSocketValid(self, _socket, now):
        """
        这条 socket 链接是否还有效
        :param _socket:
        :return:
        """

        if _socket.cacheTimeOut is not None and _socket.cacheTimeOut <= now:
            # 过期的 _socket 关闭并抛弃
            logging.debug(u'socket.cacheTimeOut 过期, socket 被关闭 ...')
            _socket.close()
            return False
        if _socket.closed:
            # 链接已经关闭
            return False

        return True


def run():
    # 服务器实例
    address = (conf_server.SERVER_IP, conf_server.SERVER_PORT)
    server = Server(address)
    logging.info('start server %s:%s ...' % address)
    server.serve_forever()


if __name__ == "__main__":
    run()

