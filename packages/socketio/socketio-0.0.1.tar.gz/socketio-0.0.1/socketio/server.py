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
    Server socket object for sending and receiving JSON messages
    """

    # Connection status
    opened = False
    clients = []

    def __init__(self, filename_or_fd, section='server'):
        err = True
        self.terminate = False
        while err:
            err = False
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
                self.message_handler = None

                # self._event_parser = EventParser(parser_config, event_subscribers)
                self._clients = []
            except Exception as ex:
                logging.error("init error in line %s: %s" % (str(sys.exc_info()[-1].tb_lineno), str(ex)))
                err = True
                time.sleep(5)
        logging.info("Socket server ready to listening")

    def start(self, message_handler):
        try:
            logging.debug("start socket server")
            self._server = asyncio.start_server(self._new_connection, self.server_ip, self.port, loop=self._loop)
            self._server = self._loop.run_until_complete(self._server)
            self.opened = True
            self.message_handler = message_handler
        except KeyboardInterrupt:
            self._loop.close()

    def broadcast_message(self, message):
        for client in self._clients:
            client.append_message(message)

    @asyncio.coroutine
    def handle_message(self, message, client):
        if message["action"] == 'ping':
            logging.debug("received ping")
            client.append_message({"action": "pong", "status": "success"})
        else:
            if self.message_handler:
                result = yield from self.message_handler(message)
                if result:
                    client.append_message(result)

    @asyncio.coroutine
    def _new_connection(self, reader, writer):
        address = writer.get_extra_info('peername')
        ip = address[0]
        if ip in self.white_list:
            client = SocketClient(address, reader, writer)
            self._clients.append(client)
            tasks = [self._loop.create_task(client.sender()), self._loop.create_task(client.receiver(self.handle_message))]
            asyncio.wait(tasks)
            while client.connected():
                try:
                    yield from asyncio.sleep(10)
                except Exception as ex:
                    logging.error("new connection error in line %s: %s" % (str(sys.exc_info()[-1].tb_lineno), str(ex)))
            client.save_all_messages()
            writer.close()
            self._clients.remove(client)
        else:
            writer.close()

    def __del__(self):
        for client in self._clients:
            client.disconnect()
