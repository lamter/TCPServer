#coding=utf-8
'''
Created on 2015-12-31

@author: Shawn
'''

from collections import OrderedDict


class LastUpdatedOrderedDict(OrderedDict):

    def __init__(self, capacity):
        super(LastUpdatedOrderedDict, self).__init__()
        self._capacity = capacity

    def __setitem__(self, key, value):
        containsKey = 1 if key in self else 0
        if len(self) - containsKey >= self._capacity:
            last = self.popitem(last=False)
            # print 'remove:', last
        if containsKey:
            del self[key]
            # print 'set:', (key, value)
        else:
            # print 'add:', (key, value)
            pass
        OrderedDict.__setitem__(self, key, value)
