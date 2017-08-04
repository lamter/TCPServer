from gevent import monkey
monkey.patch_socket()
from gevent.ssl import SSLSocket


SSLSocket
