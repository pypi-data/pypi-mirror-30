"""
Module for UNIX daemon clint and server
"""
import logging
import threading
import socket
import struct
import json
import os

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
        msg = struct.pack('>I', len(msg)) + msg
        connection.sendall(msg)
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
            data = json.loads(data)
        return data

class Sock_Client(Sock_Base):
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
        try:
            logging.info("Client conntecting to {server}".format(server=self.server_address))
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.server_address)
        except socket.error, msg:
            logging.error("Client cannot conntect to {server}: {msg}".format(server=self.server_address, msg=msg))
            return None
        # set timeout for accept to 2 seconds
        sock.settimeout(2)
        self.send_msg(sock, data)
        answer = self.recv_msg(sock)
        sock.close()
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

    def run(self):
        """
        Loop for server. Executed via `Sock_Server.start()`. 
        """
        # Bind the socket to the port
        logging.info("Server starts socket on {addr}".format(addr=self.server_address))

        # Create a UDS socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        # set timeout for accept to 2 seconds
        self.sock.settimeout(2)
        # Listen for incoming connections
        self.sock.listen(1)
        while not self.__quit.is_set():
            # Wait for incoming connections
            logging.info("Server waits for connections")
            try:
                connection, client_address = self.sock.accept()
            except socket.timeout:
                continue
            logging.info("Server received connection from {addr}".format(addr=client_address))
            data = self.recv_msg(connection)
            answer = self.request_handler(data)
            if answer is not None:
                self.send_msg(connection, answer)
            connection.close()
        self.sock.close()
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise
        return
