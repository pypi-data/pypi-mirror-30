
import unittest
from socket_client_server.socket_client_server import Sock_Server, Sock_Client
import time
import logging

class TestSockClientServer(unittest.TestCase):
    def request_handler(self, data):
        return data

    def setUp(self):
        self.server = Sock_Server("test_socket", self.request_handler)
        self.server.start()
        # Wait for server to be started
        time.sleep(1)
        self.client = Sock_Client("test_socket")
    def test_msg(self):
        data = {"test": 0, "msg": "Hallo Welt!"}
        self.assertEqual(self.client.send(data), data)
    def tearDown(self):
        self.server.quit()

class TestSockClientServerNoAnswer(unittest.TestCase):
    def request_handler(self, data):
        return None

    def setUp(self):
        self.server = Sock_Server("test_socket", self.request_handler)
        self.server.start()
        # Wait for server to be started
        time.sleep(1)
        self.client = Sock_Client("test_socket")
    def test_msg(self):
        data = {"test": 0, "msg": "Hallo Welt!"}
        self.assertEqual(self.client.send(data), None)
    def tearDown(self):
        self.server.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    unittest.main()
