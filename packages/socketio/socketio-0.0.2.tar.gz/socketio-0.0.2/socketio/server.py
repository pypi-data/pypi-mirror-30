#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
import asyncio
import logging
from configparser import ConfigParser

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)
import os.path
import sys
import netifaces as ni
from .client import SocketClient


class SocketServer:
    """
    Server socket object for manage clients and handling messages
    """

    def __init__(self, handler_functions, filename_or_fd, section='server'):
        """
        Initialize socket server object
        
        :param filename_or_fd: string or fd, file to read config from
        :param section: 
        """
        self._handler_functions = handler_functions
        self._server = None
        self.terminated = False
        self._clients = {}
        try:
            config = ConfigParser()
            if hasattr(filename_or_fd, 'read'):
                config.readfp(filename_or_fd)
            else:
                config.read(filename_or_fd)
            self.configs = dict(config.items(section))
            ni.ifaddresses('eth0')
            self.server_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
            self.port = int(self.configs["port"])
            self.white_list = self.configs["white_list"].split(", ")
            self._loop = asyncio.get_event_loop()
            logging.debug("start socket server on %s:%d" % (self.server_ip, self.port))
            server = asyncio.start_server(self._new_connection, self.server_ip, self.port, loop=self._loop)
            self._server = self._loop.run_until_complete(server)
            self._handler_functions = handler_functions
        except Exception as ex:
            logging.error("init error in line %s: %s" % (str(sys.exc_info()[-1].tb_lineno), str(ex)))
            raise ex

    def broadcast_message(self, message):
        """
        Function for broadcast message to all clients
        
        :param message: json-serializable object
        """
        for client in self._clients:
            client.append_message(message)

    @asyncio.coroutine
    def _new_connection(self, reader, writer):
        """
        Open new connection and create client
        
        :param reader: socket stream reader
        :param writer: socket stream writer
        :return: 
        """
        address = writer.get_extra_info('peername')
        ip = address[0]
        if ip in self.white_list:
            if ip in self._clients.keys():
                client = self._clients[ip]
            else:
                client = SocketClient(address, self._handler_functions)
                self._clients[ip] = client
            if not client.connected():
                client.start(reader, writer, True)
            else:
                logging.error("host %s already connected" % ip)
                writer.close()
        else:
            writer.close()

    def terminate(self):
        """
        Terminate server and all its clients
        """
        if not self.terminated:
            self.terminated = True
            self._server.close()
            for ip, client in self._clients.items():
                client.disconnect()
                del self._clients[ip]

    def __del__(self):
        self.terminate()
