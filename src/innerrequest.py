#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''

import traceback
import json


class InnerRequest(object):
    """
    实例化 socket 中获取的数据
    """
    @classmethod
    def new(cls, _json, _socket):
        try:
            dic = json.dumps(_json)
        except :
            traceback.print_exc()
            return


    def __init__(self, dic, _socket):
        """

        :param dic:
        :param _socket:
        :return:
        """


