# Copyright (C) 2018  Abhinav Saxena <abhinav.saxena@iic.ac.in>
# Institute of Informatics and Communication, University of Delhi, South Campus
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import gevent
from gevent import monkey
import socket
gevent.monkey.patch_all()  # only patch the socket for now.
# from gevent import socket

import os
import select
import sys
import serial

# gevent.monkey.patch_all() # unstable behaviour -- recheck
# import serial.rfc2217

import logging
import errno

# logger = logging.getLogger(__name__)

import logging as logger
logger.basicConfig(stream=sys.stdout, level=logging.INFO)

class SerialServer:
    """
    Serial over IP Converter -- Not RFC2217 complaint.
    Allows connecting a serial device to *any* number of TCP clients.

    (Serial Device -- RS232 or similar --) <-->  IIC4Sem  <--> (-- Network -- Client)

    :param: Tuple containing the serial connection params
    config = (name, host, port, device, baud_rate, width, parity, stop_bits, xon, rts)
    """
    def __init__(self, args, decoder=None):
        self._parse_template_obj(args, decoder)  # setup the config for one serial device per template object
        # TODO: Figure out a better way to parse the template. Using a template object is probably not a good idea
        # TODO: swap this with name, host, port, serial_params and decoder
        self._setup_tty()  # setup the serial device
        self.listener = None
        self._create_srv_socket((self.host, self.port))
        # sockets is a dictionary that is our data structure for select.poll
        # as it can be seen, the key is the file descriptor for the sockets/tty,
        # the value is the socket
        self.sockets = {
            self.listener.fileno(): self.listener,
            self.tty.fileno(): self.tty
        }

        self.addresses = {}   # a dictionary to store the client sockets info. key is the socket itself,
        # value is the client_address
        self.bytes_to_send = {}  # buffer to store data that is to be sent from serial device - for decoder
        # the key is client_address and the value would be the data supplied from the client.
        self.bytes_received = {}  # buffer to store data received from clients - for decoder
        # the key is client_address and the value would be the data supplied from the serial device for the client.

        # Setup the poller
        self.poller = select.poll()  # gevent.select.poll() - Since we are monkey_patching - unstable behaviour
        self.poller.register(self.listener, select.POLLIN)
        self.poller.register(self.tty, select.POLLIN)
        # self.rfc2217 = NotImplemented  # Initialize later

    def _parse_template_obj(self, config, decoder):
        # Change the params as per the tuple supplied
        # Get the slave settings from template
        if len(config) == 10:
            self.name = config[0]
            self.host = config[1]
            self.port = int(config[2])
            # Get the slave settings from template
            self.device = config[3]
            self.baud_rate = int(config[4])
            self.width = int(config[5])
            self.parity = config[6]
            self.stop_bits = int(config[7])
            self.xon = int(config[8])
            self.rts = int(config[9])
        elif len(config) == 5:
            self.name = config[0]
            self.host = config[1]
            self.port = int(config[2])
            # Get the slave settings from template
            self.device = config[3]
            self.baud_rate = int(config[4])
        else:
            logger.info('Incorrect serial setting detected!')
            sys.exit(3)
        self.time_out = 0  # serial connection read timeout
        self.serial_id = self.name.lower().replace(' ', '_')
        if decoder:
            namespace, _classname = decoder.rsplit('.', 1)
            module = __import__(namespace, fromlist=[_classname])
            _class = getattr(module, _classname)
            self.decoder = _class()
        else:
            self.decoder = None

        logger.info('On serial server %s - using decoder: %s', self.name, self.decoder)

    def _setup_tty(self):
        """Setup and connect to the serial device specified"""
        self.tty = serial.serial_for_url(self.device,
                                         self.baud_rate,
                                         self.width,
                                         self.parity,
                                         self.stop_bits,
                                         self.time_out,
                                         self.xon,
                                         self.rts,
                                         do_not_open=True)
        try:
            self.tty.open()
            logger.info('Connected to %s device on serial port %s', self.name, self.device)
        except serial.SerialException:
            logger.exception('Could not open serial port')
            sys.exit(3)
        # Flush input and output
        self.tty.flushInput()
        self.tty.flushOutput()

    # Some basic utility functions
    def _create_srv_socket(self, connection):
        """Build and return a listening server socket."""
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(connection)
        self.listener.listen(64)

    def start(self):
        """Start the Serial Server"""
        logger.info('Starting serial server at: %s', self.listener.getsockname())
        try:
            self.handle()
        except socket.error as se:
            if se.errno == errno.ECONNRESET:
                logger.warning('Connection reset by peer')
                pass
            elif se.errno == errno.EPIPE:
                logger.warning('Broken Pipe')
                pass
            else:
                logger.exception('Socket error on serial server %s', self.name, str(se))
                raise
        except Exception:
            logging.exception('Unexpected error occured')

    def _add_client(self, sock, address):
        """
        Add/configure a connected client socket
        :param sock: the client socket object.
        :param address: the address of the client connected. (host, port) tuple
        :param session: for databus
        """
        # TODO: Add authentication here
        sock.setblocking(False)  # this is equivalent to sock.settimeout(0.0)
        self.sockets[sock.fileno()] = sock  # Add client to our data structure
        self.addresses[sock] = address  # store the address of client
        self.poller.register(sock, select.POLLIN)  # add the client for polling

    def _remove_client(self, sock, reason='UNKNOWN'):
        """
        Remove a connected client
        :param sock: the socket object of the client
        :param session: for data bus
        :param reason: the reason for why the client disconnected
        """
        conn = self.addresses.pop(sock, None)  # remove the client_address from our dict.
        logger.info('Disconnecting client %s : %s on %s', conn, reason, self.name)
        self.poller.unregister(sock)  # remove the client from poller
        del self.sockets[sock.fileno()]  # delete the entry from our DS
        sock.close()

    def _build_request(self, client_address, raw_data):
        """
        Function to build an incoming request and add to the queue
        :param client_address:
        :param raw_data:
        :param session:
        :return:
        """
        # build request for nice request/response logs
        # we are building the request response per client_address.
        self.bytes_received[client_address] = raw_data  # make sure poller does not misbehave
        # TODO: clean the incoming data. If the data is crc_validated, add it to the queue, else add it
        # TODO: buffers.
        logger.info('Received data from client: %s - %s', client_address, raw_data.encode('string-escape'))

    def _build_response(self, client_address, raw_data):
        """
        Function to build a
        :param client_address: (host, port) tuple
        :param raw_data: the data that is received from the serial device
        :param session: for databus
        """
        # build response for nice request/response logs
        # having and adding to buffers only required when we need request/response logs
        # so first we check whether the decoder exists or not.
        if self.decoder:
            # if the client_address is already present, we have only received part of the response from
            # serial device
            if client_address in self.bytes_to_send:
                # if that is the case, just append the raw_data received to the buffer.
                self.bytes_to_send[client_address] += raw_data  # TODO: This is probably a bad idea. Use bytearray instead
            else:
                # if not, then this is first time a client has sent some data,
                # add the client and the data to the buffer
                self.bytes_to_send[client_address] = raw_data
            logger.debug('Response data from serial device: %s - %s', self.device,
                         self.bytes_to_send[client_address].encode('string-escape'))
            # TODO: Add check if data if crc_validated and add it to a queue. queue in the dictionary bytes_to_send.
            # TODO: This queue would be outgoing_queue. Producer being tty and consumers being clients
        else:
            self.bytes_to_send[client_address] = raw_data  # make sure poller does not misbehave if decoder not present
            logger.info('Response data from serial device: %s - %s', self.device, raw_data.encode('string-escape'))

    def _parse_request_response(self, client_address):
        """
        Function that checks whether the packet in buffers is valid, logs request and response
        :param client_address: (host, port) pair of socket
        :param session:  for data bus
        """
        if self.decoder:
                try:
                    # to properly parse the request, response, we need to check if data in the buffers mean anything
                    # to the decoder. Hence a condition to validate the crc of the data in buffer.
                    if self.decoder.validate_crc(self.bytes_to_send[client_address]):
                        # if data in buffers is valid, pop the contents of the buffers for that particular client address
                        # and decode the contents of the buffers.
                        rb = self.decoder.decode(self.bytes_received.pop(client_address, b''))
                        sb = self.decoder.decode(self.bytes_to_send.pop(client_address, b''))
                        logger.info(
                            'Traffic on serial device {2} from client {3} -\n Request: {0},\n Response: {1}'.format(
                                rb, sb, self.name, (client_address, )))
                except KeyError:
                    logger.exception('Key Error: client address does not exist')
                except Exception:
                    logger.exception('On serial server %s - error occurred while decoding', self.name)

    def _all_events(self):
        while True:
            for fd, event in self.poller.poll(500):  # wait 500 milliseconds before selecting
                yield fd, event

    def handle(self):
        """Handle connections and manage the poll."""
        session = None  # for databus
        for fd, event in self._all_events():
            sock = self.sockets[fd]  # so a sock would be the socket of any client or listener or serial device

            # If socket is closed: remove from the DS
            if event & (select.POLLHUP | select.POLLERR):
                # the buffer contents are not longer needed to be in the buffers
                # for the same, we need to find the client_address. Furthermore, the client also has to be purged from
                # the address dict. Hence, pop the entry from the dict.
                address = self.addresses[sock]
                # pop the contents of the buffers
                sb = self.bytes_to_send.pop(address, b'')
                if sb:
                    logger.info('On serial server %s - client %s closed before we sent %s', self.name, address,
                                sb.encode('string-escape'))
                    self._remove_client(sock, 'CONNECTION_LOST')
                else:
                    rb = self.bytes_received.pop(address, b'')
                    logger.info('On serial server %s - client %s sent %s but then closed', self.name, address,
                                rb.encode('string-escape'))
                    self._remove_client(sock, 'CONNECTION_QUIT')

            # Incoming data from either a serial device or a client
            elif event & select.POLLIN:
                # New Socket: A new client has connected
                if sock is self.listener:
                    client_sock, address = sock.accept()
                    # For new client, start the databus session.
                    self._add_client(client_sock, address)

                # check whether sock is client or serial device
                elif sock is self.tty:
                    try:
                        # read from serial device
                        data = sock.read(80)
                        if not data:
                            raise serial.SerialException
                        else:
                            for client_sock in self.addresses.keys():
                                logger.info('Received data from serial device for client: %s - %s',
                                            self.addresses[client_sock], data.encode('string-escape'))
                                client_sock.send(data)
                                # TODO: get data from the outgoing_queue. and send it.
                                # Note that if client disconnected before send, a broken pipe error would be logged
                                if self.decoder:
                                    self._build_response(self.addresses[client_sock], data)
                                    self._parse_request_response(self.addresses[client_sock])
                    except socket.timeout:
                        logger.exception('Client Timed out on serial server %s', self.name)
                    except socket.error as se:
                        if se.errno == errno.ECONNRESET:
                            logger.warning('Connection reset by peer')
                            raise
                        elif se.errno == errno.EPIPE:
                            logger.warning('Broken Pipe')
                            raise
                        else:
                            logger.exception('Socket error on serial server %s', self.name, str(se))

                else:
                    # sock is a client sending in some data
                    data = sock.recv(80)
                    if not data:  # end of file
                        # remove the client and close the databus session
                        logger.info('On serial server %s - client %s closed socket normally', self.name, self.addresses[sock])
                        self._remove_client(sock, 'CONNECTION_TERMINATED')
                        # next poll() would be POLLNVAL, and thus cleanup
                        continue
                    else:
                        try:
                            self._build_request(self.addresses[sock], data)
                            # TODO: get data from the incoming queue and write it to the serial device

                            self.tty.write(data)
                        except serial.SerialTimeoutException:
                            logger.exception('Serial Timeout Reached')

    def stop(self):
        """Stop the Serial Server"""
        logger.info('Stopping serial-server %s:%s', self.host, self.port)
        for client in self.addresses.keys():
            client.close()
        logger.info('Closing the serial connection for %s on %s', self.name, self.device)
        self.tty.close()
        self.listener.shutdown(socket.SHUT_RDWR)
        self.listener.close()


# For debugging
if __name__ == '__main__':
    # (name, host, port, device, baud_rate)
    test_config = ('test', '0.0.0.0', 16003, '/dev/tty/ACM0', 9600)
    logger.info('Starting Serial Server')
    test_server = SerialServer(test_config)
    try:
        server.start()
    except Exception:
        logging.exception('Error Occurred!')
        sys.exit(1)
