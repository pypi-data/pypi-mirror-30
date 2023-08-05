import gevent
from gevent import monkey
monkey.patch_all()

import sys
import logging
from gevent.server import StreamServer
import logging as logger

logger = logging.getLogger(__name__)
# For debugging --
# logger.basicConfig(stream=sys.stdout, level=logging.INFO)

class LibeventServer:
    """
    Simple Libevent Based Server capable of handling multiple clients at a time.
    In python, we are using gevent which is python's port to Libevent library
    """
    def __init__(self):
        self.server = None  # Initialize later

    def handler(self, client_socket, client_address):
        """Handles the incoming client connection"""
        logger.info('Incoming Connection from client:', client_address)
        client_socket.sendall(b'Welcome to the echo server! Type quit to exit.\r\n')
        # using a makefile because we want to use readline()
        rfileobj = client_socket.makefile(mode='rb')
        while True:
            line = rfileobj.readline()
            if not line:
                logger.info("Client disconnected")
                break
            if line.strip().lower() == b'quit':
                logger.info("Client quit")
                break
            client_socket.sendall(line)
            logger.info("Echoed %r",line)
        rfileobj.close()

    def start(self, host, port):
        """Starts the Libevent Web server"""
        conn = (host, port)
        self.server = StreamServer(conn, self.handler)
        try:
            logger.info('Starting Libevent Server on port 16000')
            self.server.serve_forever()
        except:
            self.stop()

    def stop(self):
        """Stops the Libevent Server"""
        logger.info('Stopping Libevent Server')
        self.server.close()

if __name__ == '__main__':
    test = LibeventServer()
    try:
        test.start('127.0.0.1', 16000)
    except KeyboardInterrupt:
        logger.info('Stopping Libevent Server!')
    finally:
        test.stop()
