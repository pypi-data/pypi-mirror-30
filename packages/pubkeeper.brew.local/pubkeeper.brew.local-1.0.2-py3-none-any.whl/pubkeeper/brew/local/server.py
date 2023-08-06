"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.logging import get_logger
from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer


class LocalBrewServer(TCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
        self.connected_streams = []

    def handle_stream(self, stream, addr):
        self.connected_streams.append(stream)

    @gen.coroutine
    def write_all(self, data):
        closed = []
        for stream in self.connected_streams:
            try:
                ret = yield stream.write(data)
                if ret is not None:
                    closed.append(stream)
            except StreamClosedError:
                closed.append(stream)

        for closed_stream in closed:
            self.connected_streams.remove(closed_stream)
