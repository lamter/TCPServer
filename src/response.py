#coding=utf-8
'''
Created on 2015-10-25

@author: Shawn
'''

import traceback
import json



class BaseResponse(object):
    """
    实例化响应
    """
    REQUEST_TEST = 10001
    REQUEST_UNVALID = 10002

    def __init__(self, tag, _type, _socket, server):
        self.socket = _socket
        self.server = server
        self.tag = tag
        self.type = _type
        self.data = {
            'tag': self.tag,
            'type': self.type,
        }


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



class UnvalidRequestData(BaseResponse):
    """
    无效的请求数据
    """

    def __init__(self, tag, _socket, server):
        BaseResponse.__init__(self, tag, BaseResponse.REQUEST_UNVALID, _socket, server)

