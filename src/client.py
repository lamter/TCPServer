#coding=utf-8
'''
Created on 2015-10-23

@author: Shawn
'''

from gevent.monkey import patch_all
patch_all()
from socket import socket
from gevent.queue import Queue
import gevent.socket

import conf_server

queue = Queue()

queue.put('123')
queue.put('456')

print(queue.peek())
print(queue.peek())


import json
print(json.loads('123'))



# address = (conf_server.SERVER_IP, conf_server.SERVER_PORT)
# s = socket()
# s.connect(address)
#
# print s.recv(1024)
# s.send('123')
# print s.recv(1024)
#
# queue.put(s)
#
# s.close()
