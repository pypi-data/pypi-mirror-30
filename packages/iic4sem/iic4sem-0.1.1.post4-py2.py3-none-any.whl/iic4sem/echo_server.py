"""
Simple Echo Server capable of handling only one client at a time.
"""
import socket
import sys
import logging
logger = logging.getLogger(__name__)

# For debugging --
# import logging as logger
# logger.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class EchoServer:
    def __init__(self):
        logger.info('Initializing Simple Echo Server!')
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # our connection handler.
    def handler(self, client_sock, client_address):
        """Handles the incoming client connection"""
        logger.info('client connected: ', client_address)
        while True:
            data = client_sock.recv(1024)
            logger.info('Received data: ', data)
            if data:
                client_sock.sendall(data)
            else:
                break

    def start(self, host, port):
        """Starts the Echo server"""
        conn = (host, port)
        # TCP connection
        self.listener.bind(conn)
        # how many connections do we want to allow? This would go in sock.listen
        self.listener.listen(16)
        while True:
            logger.info('EchoServer waiting for a connection on {}'.format(conn))
            try:
                client_sock, client_address = self.listener.accept()
                self.handler(client_sock, client_address)
            finally:
                self.stop()

    def stop(self):
        """Stops the Echo Server"""
        # Maybe shutdown the socket?
        self.listener.close()

# For infoging
if __name__ == '__main__':
    test = EchoServer()
    try:
        logger.info('Starting Echo Server!')
        test.start('', 4443)
    except KeyboardInterrupt:
        logger.info('Stopping Echo Server!')
