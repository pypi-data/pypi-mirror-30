# The MIT License (MIT)
#
# Copyright (c) 2018 James K Bowler, Data Centauri Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from datetime import datetime, timedelta
from random import randint

import socket 
import json
import struct


class ClientExample(object):
    def __init__(self):
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.ip = "127.0.0.1"
        self.port = 60312
        self.dummy_payload = []
        self.dt = datetime.utcnow()
        insert = "REPLACE INTO {0}.{1} ".format('db_name', 'tb_name')
        stmt = """(date, open, high, low, close, volume
                  ) VALUES (%s, %s, %s, %s, %s, %s);"""
        self._sql = insert + stmt
        
    def dummy(self):
        dummy_payload = []
        rand = randint(1, 300)
        for i in range(rand):
            self.dt+=timedelta(minutes=1)
            data = [datetime.strftime(self.dt, '%Y-%m-%d %H:%M:%S.%f'), 1.3991 , 1.40706, 1.39288, 1.39702, 306833]
            dummy_payload.append(data)
        return dummy_payload
    
    def get_client_socket(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.ip, self.port))
        return client
    
    def create_message(self, id, payload, sql):
        identifer = "{}_{}".format(self.__class__.__name__, str(id))
        msg = {"identifer": identifer, "payload": payload, "query": sql}
        message = json.dumps(msg).encode()
        message = struct.pack('>I', len(message)) + message
        return message

    def send_exit_msg(self):
        client = self.get_client_socket()
        message = self.create_message(0, "exit", "None")
        client.sendall(message)
        client.recv(4096)
        
    def data(self):
        for i in range(1, 1000):
            client = self.get_client_socket()
            message = self.create_message(i, self.dummy(), self._sql)
            client.sendall(message)
            client.recv(4096)
        self.send_exit_msg()
        
    def run(self):
        self.data()
        
        
ClientExample().run()