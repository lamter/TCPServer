#coding=utf-8
'''
Created on 2015-10-25

@author: Shawn
'''

import traceback
import json

import serverdata


class BaseResponse(object):
    """实例化响应"""

    NOT_NEED_SAVE_TYPE = []

    REQUEST_TEST = 10001
    REQUEST_UNVALID = 10002

    def __init__(self, tag, _type, _socket):
        self.socket = _socket
        self.tag = tag
        self.type = _type
        self.data = {
            'tag': self.tag,
            'type': self.type,
        }

    @property
    def server(self):
        return serverdata.serverData.server


    def json(self):
        """

        :return:
        """

        return json.dumps(self.data)


    def send(self):
        """
        调用 server.sendResponse 来发送数据
        :return:
        """
        self.server.sendResponse(self)


    def __str__(self):
        s = object.__str__(self)
        return s.strip('>') + ' tag:%s type:%s doc:%s' % (self.tag, self.type, self.__doc__) + '>'


    def isNeedSaveCache(self):
        """
        调用 server.sendResponse 来发送数据
        :return:
        """
        return not self.type in self.NOT_NEED_SAVE_TYPE



class UnvalidRequestData(BaseResponse):
    """
    无效的请求数据
    """

    def __init__(self, tag, _socket):
        BaseResponse.__init__(self, tag, BaseResponse.REQUEST_UNVALID, _socket)


class ResponseTest(BaseResponse):
    """响应测试协议"""

    def __init__(self, tag, _socket):
        BaseResponse.__init__(self, tag, BaseResponse.REQUEST_TEST, _socket)

        self.data['text'] = 'response success ...'