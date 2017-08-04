#coding=utf-8
'''
Created on 2015-12-30

@author: lamter
'''

# from gevent import monkey
# monkey.patch_all()

import time
import unittest
import json

import socket
from mynetwork import *

import conf_server
import conf_debug
from request import BaseRequest


''' 建立 redisco 的链接 '''

class TestSocket(unittest.TestCase):
    '''
    测试
    '''
    def setUp(self):
        self.host, self.port = 'localhost', 8912
        self.address = (self.host, self.port)
        self.socket = socket.socket()
        self.socket.connect(self.address)

        # 压力测试
        self.sockets = {}



    def tearDown(self):
        self.socket.close()


    def test_sendRequest(self):
        """
        发送一个测试请求
        :return:
        """
        dic = {
            'tag': 101,
            'type': BaseRequest.REQUEST_TEST,
        }

        _json = json.dumps(dic)


        data = dumpInt32(_json, conf_server.AES_KEY)

        self.socket.sendall(data)

        print(loadInt32(self.socket, conf_server.AES_KEY))


    def test_receiveCache(self):
        """
        测试通过缓存返回
        :return:
        """

        dic = {
            'tag': 101,
            'type': BaseRequest.REQUEST_TEST,
        }

        _json = json.dumps(dic)

        data = dumpInt32(_json, conf_server.AES_KEY)

        # 发送两次
        self.socket.sendall(data)
        self.socket.sendall(data)

        print(loadInt32(self.socket, conf_server.AES_KEY))
        time.sleep(1)


