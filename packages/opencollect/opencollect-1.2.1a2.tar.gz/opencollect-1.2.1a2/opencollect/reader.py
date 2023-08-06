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
from collections import namedtuple
from threading import Thread
import json
import time
import socket
import struct


class SocketsStreamReader(object):
    """
    A class representing a none blocking SocketsStreamReader.
    It contains an id for tracking with the ability
    to handle different types of streamed events.

    Parameters
    ----------
    port       : TCP port number
    host       : IP Address
    identifier : human-readable identifier
    
    Exposes
    -------
    read_buffer()
    
    """
    def __init__(
        self,
        port=60312,
        host="0.0.0.0",
        identifer="Terminator"
    ):
        self.id = identifer
        self._buffer = []
        self._stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self._stream.bind((host, port))
        self._stream.listen(5)
        
        def _stream_to_buffer(id, stream, buffer):
            """
            Stream reading.
            """
            def handle(id, sock, buffer):
                def recv_msg(sock):
                    """
                    Get the message
                    """
                    raw_msglen = recvall(sock, 4)
                    if not raw_msglen:
                        return None
                    msglen = struct.unpack('>I', raw_msglen)[0]
                    return recvall(sock, msglen)

                def recvall(sock, n):
                    """
                    Piece large data
                    """
                    data = b''
                    while len(data) < n:
                        packet = sock.recv(n - len(data))
                        if not packet:
                            return None
                        data += packet
                    return data
                
                def container(result):
                    """
                    Container for payload
                    """
                    sm = json.loads(result.decode())
                    if not isinstance(sm, dict):
                        raise AttributeError("Loaded json must be a dict")
                    keys = sm.keys()
                    if 'identifer' not in keys:
                        raise KeyError("no identifer found!")
                    if 'payload' not in keys:
                        raise KeyError("no payload found!")
                    if 'query' not in keys:
                        raise KeyError("no query found!")
                    if len(keys) > 3:
                        raise AttributeError("Unexpected key in dict")
                    DataTuple = namedtuple(sm['identifer'], ['identifer', 'payload', 'query'])
                    return DataTuple(**sm)

                result = recv_msg(sock)
                sock.send(b'ACK!')
                sock.close()
                if result:
                    buffer.append(container(result))
                else:
                    raise EOFError(
                        "Unexpected End of Stream {}".format(id)
                    )

            while True:
                try:
                    sock = stream.accept()[0]
                except OSError:
                    print("Shutting down SocketsStreamReader")
                    break
                client_handler = Thread(
                    target=handle,
                    args=(id, sock, buffer)
                )
                client_handler.start()

        self.t = Thread(
            target=_stream_to_buffer,
            args=(self.id, self._stream, self._buffer,)
        )
        self.t.daemon = True
        self.t.start()

    def close_session(self):
        """
        Close socket
        """
        self._stream.shutdown(socket.SHUT_WR)
        time.sleep(2)
        self._stream.close()
        
    def read_buffer(self, sleepy_time=0.00001):
        """
        Read items first item and removes from the
        the list. (FIFO)
        
        Returns
        -------
        namedtuple
        
        """
        try:
            return self._buffer.pop(0)
        except IndexError:
            return time.sleep(sleepy_time)
