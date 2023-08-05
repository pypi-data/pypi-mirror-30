import six
if six.PY2:
	from socket_client_server import Sock_Server, Sock_Client
else:
	from socket_client_server.socket_client_server import Sock_Server, Sock_Client
