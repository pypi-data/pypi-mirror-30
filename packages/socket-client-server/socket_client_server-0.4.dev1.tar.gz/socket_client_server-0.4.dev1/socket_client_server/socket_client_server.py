"""
Module for UNIX daemon clint and server
"""
import logging
import threading
import socket
import struct
import json
import os

# compatibility with 2.7 and 3.6
import future
import builtins
import past
import six
from contextlib import closing

class Sock_Base:
    """
    Bass class for client and server
    """
    def __init__(self, server_address):
        self.server_address = server_address
    def send_msg(self, connection, data):
        """
        Function to send messages
        
        Parameters
        ----------
        connection: socket or connection
        data: data that can be serialized to json
        """
        # serialize as JSON
        msg = json.dumps(data)
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)).decode() + msg
        connection.sendall(msg.encode())
        return

    def recv_msg(self, connection):
        """
        Function to receive messages

        Parameters
        ----------
        connection: socket or connection

        Return value
        ------------
        message received as dictionary
        """
        # Read message length and unpack it into an integer
        raw_msglen = self.__recvall(connection, 4, decode_json=False)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.__recvall(connection, msglen)

    def __recvall(self, connection, n, decode_json=True):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = connection.recv(n - len(data))
            if not packet:
                return None
            data += packet
        # deserialize JSON
        if decode_json:
            data = json.loads(data.decode())
        return data

class Sock_Client(Sock_Base):
    def sending(self, sock, data):
        sock.connect(self.server_address)
        # set timeout for accept to 2 seconds
        sock.settimeout(2)
        logging.debug("Sending...")
        self.send_msg(sock, data)
        logging.debug("Message send")
        answer = self.recv_msg(sock)
        logging.debug("Answer received")
        return answer
    """
    Class for clients
    """
    def send(self, data):
        """
        Send date to server

        Parameters
        ----------
        data: object that can be serialized to JSON
        """
        answer = None
        try:
            logging.info("Client conntecting to {server}".format(server=self.server_address))
            if six.PY2:
                sock = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
                answer = self.sending(sock, data)
                sock.close()
            else:
                with socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM) as sock:
                    answer = self.sending(sock, data)

        except socket.error as e:
            logging.error("Client cannot conntect to {server}: {msg}".format(server=self.server_address, msg=e.strerror))
            return None

        return answer



class Sock_Server(Sock_Base, threading.Thread):
    """
    Class for server

    Started with `Sock_Server.start()`, stop with
    `Sock_Server.quit()`.
    """
    def __init__(self, server_address, request_handler):
        """
        Parameters
        ==========
        server_address:  socket address

        request_handler: function with one string parameter for
            incoming message returning return message or None
        """
        # Make sure the socket does not already exist
        threading.Thread.__init__(self)

        try:
            os.unlink(server_address)
        except OSError:
            if os.path.exists(server_address):
                raise

        Sock_Base.__init__(self, server_address)
        self.request_handler = request_handler
        self.__quit = threading.Event()
    def quit(self):
        """
        Quit socket server
        """
        logging.info("quiting sock server")
        if self.__quit is not None:
            self.__quit.set()
        self.join()
        return

    def listen(self, sock):
        sock.bind(self.server_address)
        # set timeout for accept to 2 seconds
        sock.settimeout(2)
        # Listen for incoming connections
        sock.listen(1)
        while not self.__quit.is_set():
            # Wait for incoming connections
            logging.debug("Server waits for connections")
            try:
                connection, client_address = sock.accept()
            except socket.timeout:
                continue
            logging.info("Server received connection from {addr}".format(addr=client_address))
            data = self.recv_msg(connection)
            logging.info("Server received data {data}".format(data=data))
            answer = self.request_handler(data)
            if answer is not None:
                self.send_msg(connection, answer)
            connection.close()

    def run(self):
        """
        Loop for server. Executed via `Sock_Server.start()`. 
        """
        # Bind the socket to the port
        logging.info("Server starts socket on {addr}".format(addr=self.server_address))

        # Create a UDS socket
        if six.PY2:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.listen(sock)
            sock.close()
        else:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                self.listen(sock)
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise
        return
