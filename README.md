# TCPServer
A TCP server based on gevent stream server.

## How to Start
In production environment, start server as :
		cd TCPserver/sh
		sh start_server.sh
and stop server as :
		sh stop_server.sh

Clearly, pid file under floder TCPServer/tmp.

In other way, you can
		python server.py
direactly. By This way, conf_debug will be available which you can rest argument in conf_server.