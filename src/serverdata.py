#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''


global serverData


class ServerData(object):
    """

    """
    def __init__(self, server):
        global serverData
        serverData = self

        ''' 服务器实例 '''
        self.server = server


