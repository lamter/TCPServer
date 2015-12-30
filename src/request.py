#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''

import traceback
import json
import logging

from error import *
import response
import serverdata

class BaseRequest(object):
    """
    实例化 socket 中获取的数据
    """
    REQUEST_TEST = '10001'

    @classmethod
    def new(cls, dic, _socket):
        try:
            _type = dic.get('type')
            RequestClass = cls.getClassByType(_type)

            return RequestClass(dic, _socket)

        except:
            logging.error(traceback.format_exc())


    @classmethod
    def getClassByType(cls, _type):
        """
        :param _type:
        :return:
        """

        if _type == cls.REQUEST_TEST:
            return Test
        else:
            return UnvalidRequestData


    def doIt(self):
        """
        :return:
        """
        raise FunctionUndefind(self.doIt)


    def __init__(self, dic, _socket):
        """

        """
        self.tag = dic.get('tag')
        self.data = dic
        self.socket = _socket


    @property
    def server(self):
        return serverdata.serverData.server



class UnvalidRequestData(BaseRequest):
    """
    无效的请求类型
    """
    def doIt(self):
        """
        """
        logging.debug("无效的请求类型:%s" % self.data.get('type'))
        response.UnvalidRequestData(self.tag, self.socket).send()



class Test(BaseRequest):
    """
    测试用的请求
    """

    def doIt(self):
        """

        :return:
        """

        # 给 socket 绑定实例
        logging.debug('给 socket 绑定实例: True')
        serverdata.serverData.server.socketLink(self.socket, True)

        logging.info('这是一个测试用的协议')

        response.ResponseTest(self.tag, self.socket).send()