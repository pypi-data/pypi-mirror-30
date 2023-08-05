"""
Simple Broadcast Server capable of handling multiple clients
"""
import gevent
from gevent import monkey
monkey.patch_all()
import socket
import sys
import logging
from gevent.server import StreamServer

logger = logging.getLogger(__name__)
# For debugging --
# import logging as logger
# logger.basicConfig(stream=sys.stdout, level=logging.INFO)

class BroadcastServer:
    def __init__(self, message=None):
        self.message = message
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = dict()

    def handler(self, client_socket, client_address):
        """Handles the incoming client connection"""
        self.clients[client_address] = client_socket
        logger.info('Incoming Connection from client {}:{}'.format(client_address[0], client_address[1]))
        client_socket.sendall(b'Welcome to the broadcast server! Type quit to exit.\r\n')
        # using a makefile because we want to use readline()
        rfileobj = client_socket.makefile(mode='rb')
        while True:
            line = rfileobj.readline()
            for client in self.clients.items():
                if client[0] == client_address:
                    text = b'You have entered:  ' + line
                    client_socket.sendall(text)
                else:
                    text = 'client {} has entered data: {}'.format(client_address, line.decode())
                    client[1].sendall(text.encode())
            if not line:
                logger.info("Client {}:{} disconnected".format(client_address[0], client_address[1]))
                break
            if line.strip().lower() == b'quit':
                logger.info("Client {}:{} quit".format(client_address[0], client_address[1]))
                break
            # client_socket.sendall(line)
            logger.info("Echoed %r from client %s:%s",line, client_address[0], client_address[1])
        rfileobj.close()

    def start(self, host, port):
        """Starts the Broadcast Web server"""
        conn = (host, port)
        self.listener = StreamServer(conn, self.handler)
        try:
            logger.info('Starting BroadcastServer on {}'.format(conn))
            self.listener.serve_forever()
        except:
            self.stop()

    def stop(self):
        """Stops the Broadcast Server"""
        logger.info('Stopping Broadcast Server')
        self.listener.close()

if __name__ == '__main__':
    test = BroadcastServer()
    try:
        test.start('127.0.0.1', 16000)
    except KeyboardInterrupt:
        logger.info('Stopping Broadcast Server!')
    finally:
        test.stop()
