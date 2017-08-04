#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''

from gevent import monkey
monkey.patch_all()

import json
import datetime
import functools
import traceback
import signal
import logging

from mynetwork import *

import gevent
from gevent import sleep
from gevent.server import StreamServer
from gevent.pool import Pool
from gevent.queue import Queue

import server.conf_server as conf_server
if __name__ == "__main__":
    import conf_debug

import server.comment as comment
import log
from server.serverdata import ServerData
from server.request import BaseRequest



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
                func(*args, **kw)
                sleep(0)    # 完成之后跳转
        except gevent.GreenletExit:
            logging.info('stop forever %s ...' % func.__name__)

    return wrapper



class Server(StreamServer):
    """
    socket 服务器
    """
    def __init__(self, address):
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

        # 尚未绑定实例, 用这个属性来绑定实例
        _socket.link = None

        # 是否绑定一个实例
        _socket.isLink = lambda: _socket.link is not None

        # 响应缓存
        _socket.responseCache = {}      # {tag: response}

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
        # for _ in xrange(self.sockets.qsize()):
        self.pool.map(self._recv, self.sockets)


    def _recv(self, _socket):
        isValid = False
        try:
            isValid = self.isSocketValid(_socket)
            if not isValid:
                # 检查链接是否有效
                return

            # 采用Int32位，解密解压出数据，可根据需求更改
            AES_KEY = self.get_AES_KEY()
            try:
                _json = loadInt32(_socket, AES_KEY)
            except:
                isValid = False
                raise

            if not _json:
                # 没有收到数据
                return

            logging.debug(u'receive from %s:%s \n%s' % (_socket.host,_socket.port, _json))

            data = json.loads(_json)
            if not isinstance(data, dict):
                raise ValueError('unvaild json data ...')

            # 返回响应缓存
            if _socket.isLink():
                ''' 绑定了实例才返回缓存 '''
                _response = self.getResponseCache(_socket, data)
                if _response:
                    ''' 直接返回响应 '''
                    _response.send()
                    logging.debug(u'返回缓存 response cache, data : %s' % data)
                    return
                elif self.isHaveRequest(_socket, data):
                    ''' 已经在处理这个请求，还没生成响应，则跳过 '''
                    return

                    # 业务逻辑处理，此处可重构
            self.async(data, _socket)

        except gevent.GreenletExit:
            raise
        except gevent.socket.error:
            _socket.close()
            logging.info(u'关服，关闭当前的 socket ...')
        except:
            logging.error(u'receive from %s:%s \n%s' % (_socket.host, _socket.port, traceback.format_exc()))
        finally:
            if isValid:
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

        # 关闭所有的 socket
        self.closeSockets()

        # 关闭日志模块
        logging.shutdown()

        # 关闭服务器
        self.close()


    def async(self, dic, _socket):
        """
        异步模式的业务处理，并发业务
        :param dic: 传入的数据需要为 dic 格式
        :param _socket:
        :return:
        """


        # 实例化 request
        r = BaseRequest.new(dic, _socket)

        # 保存 tag
        self.saveRequestTag(_socket, r.tag)

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

        # 保存响应缓存
        if _socket.isLink() and _response.isNeedSaveCache():
            # 绑定了实例，并且属于需要保存缓存的， 保存响应缓存
            self.saveResponseCache(_socket, _response)

        # json 格式的数据
        _json = _response.json()

        # 加压加密
        AES_KEY = self.get_AES_KEY()
        data = dumpInt32(_json, AES_KEY)

        # logging.debug('send dat to %s:%s dat:\n' % (_socket.host, _socket.port) + data)

        def _send(_socket, data):

            try:
                # 发送数据
                _socket.sendall(data)
            except:
                err = 'Send dat to %s:%s faild. data len:%s err:\n' % (_socket.host, _socket.port, len(data))
                err += traceback.format_exc()
                logging.error(err)
                # 出错后断开这条 socket
                _socket.close()

        # 并发这条发送
        self.spawn(_send, _socket, data)


    def isSocketValid(self, _socket):
        """
        这条 socket 链接是否还有效
        :param _socket:
        :return:
        """

        if _socket.cacheTimeOut is not None and _socket.cacheTimeOut <= datetime.datetime.now():
            # 过期的 _socket 关闭并抛弃
            logging.info(u'socket.cacheTimeOut 过期, socket %s:%s 被关闭 ...' % (_socket.host, _socket.port))
            _socket.close()
            return False
        if _socket.closed:
            # 链接已经关闭
            return False

        return True


    def socketLink(self, _socket, link):
        """
        给 socket 绑定一个实例
        :param _socket:
        :param link:
        :return:
        """
        _socket.link = link

        # 重设响应缓存，及其缓存数量
        _socket.responseCache = comment.LastUpdatedOrderedDict(conf_server.RESPONSE_CACHE_SIZE)


    def saveRequestTag(self, _socket, tag):
        """
        先保存到这个 tag
        :param _socket:
        :param tag:
        :return:
        """
        _socket.responseCache[tag] = None


    def saveResponseCache(self, _socket, _response):
        """
        :return:
        """
        logging.debug('保存 response cache : %s' % _response)
        _socket.responseCache[_response.tag] = _response


    def getResponseCache(self, _socket, data):
        """
        :param _socket:
        :param data:
        :return: _response
        """

        return _socket.responseCache.get(data.get('tag'))


    def isHaveRequest(self, _socket, data):
        """
        已经在处理这个请求了，还没生成 response
        :param _socket:
        :param data:
        :return: _response
        """

        return data.get('tag') in _socket.responseCache


    def closeSockets(self):
        """
        关闭所有 socket
        :return:
        """

        logging.info(u'即将关闭 %s 个 socket 链接...' % self.sockets.qsize())
        while not self.sockets.empty():
            s = self.sockets.get_nowait()
            s.close()



def run():
    # 服务器实例
    address = (conf_server.SERVER_IP, conf_server.SERVER_PORT)
    server = Server(address)
    logging.info('start server %s:%s ...' % address)
    server.serve_forever()


if __name__ == "__main__":
    run()

