#coding=utf-8
'''
Created on 2015-10-23

@author: lamter
'''


from optparse import OptionParser

import conf_server

parser = OptionParser()
parser.add_option("-a", "--arg",
                  dest="arg",
                  help="Rewrite this arg.",
                  type="string",
                  )

(options, args) = parser.parse_args()


# 设置参数
conf_server.ARG = options.arg


if __name__ == "__main__":
    import tcpserver
    tcpserver.run()