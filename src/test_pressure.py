#coding=utf-8
'''
Created on 2015-12-31

@author: lamter
'''

from gevent import monkey
monkey.patch_all()

import time
import unittest
import json

from gevent.pool import Group
import socket
from lib.woodmoo import *

import conf_server
import conf_debug
from request import BaseRequest


''' 建立 redisco 的链接 '''

class TestPressure(unittest.TestCase):
    '''压力测试'''
    def setUp(self):

        # 压力测试
        self.sockets = {}
        self.socketNum = 500
        self.address = self.host, self.port = 'localhost', 8912

        # 生成 socket 实例
        for i in range(self.socketNum):
            self.sockets[i] = socket.socket()


    def tearDown(self):

        for s in  self.sockets.itervalues():
            if not s.closed:
                s.close()


    def test_pressure(self):
        """
        :return:
        """
        # 全部建立链接
        for s in self.sockets.itervalues():
            s.connect(self.address)

        dic = {
            'tag': 101,
            'type': BaseRequest.REQUEST_TEST,
        }

        _json = json.dumps(dic)

        data = dumpInt32(_json, conf_server.AES_KEY)

        send = lambda s:s.sendall(data)

        recv = lambda s:s.recv(1024)

        # 第一次 并发发送数据
        Group().map(send, self.sockets.itervalues())

        # 第二次 并发发送数据
        Group().map(send, self.sockets.itervalues())

        # 第一次 收取数据
        print Group().map(recv, self.sockets.itervalues())

        # 第二次 收取数据
        print Group().map(recv, self.sockets.itervalues())





