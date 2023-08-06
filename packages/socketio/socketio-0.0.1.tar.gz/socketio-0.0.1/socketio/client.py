#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import asyncio
import logging
import uuid
import os
import time

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)
import os.path
import sys
SOCKET_PING_INTERVAL = 30


class SocketClient:

    def __init__(self, address, handler_functions, reader=None, writer=None):
        self._host = address[0]
        self._port = address[1]
        self._reader = reader
        self._writer = writer
        self._handler_functions = handler_functions
        self._loop = asyncio.get_event_loop()
        self._message_queue = asyncio.Queue(loop=self._loop)
        self.load_saved_messages()
        self._connected = False
        self._terminate = False
        self.ponged = True
        self.wait_responses = {}

    @asyncio.coroutine
    def start(self):
        while not self._terminate:
            if not self._connected:
                logging.debug("connecting to server %s" % self._host)
                try:
                    self._reader, self._writer = yield from asyncio.open_connection(self._host, self._port,
                                                                                    loop=self._loop)
                    self._connected = True
                    tasks = [self._loop.create_task(self.sender()), self._loop.create_task(self.receiver()), self._loop.create_task(self.pinger())]
                    wait_tasks = asyncio.wait(tasks)
                except OSError:
                    logging.error("connection to server %s failed!" % self._host)
                    self._connected = False
            yield from asyncio.sleep(2.0)

    @asyncio.coroutine
    def receiver(self):
        logging.info("start receiver on %s" % self._host)
        while self.connected():
            try:
                message = yield from self.receive_json()
                if message:
                    if "action_id" in message.keys():
                        if message["action_id"] in self.wait_responses.keys():
                            future = self.wait_responses.pop(message["action_id"])
                            future.set_result(message)
                    if message["action"] == 'pong':
                        self.ponged = True
                    if message["action"] in self._handler_functions.keys():
                        print("start handling")
                        self._handler_functions[message["action"]](message)
            except Exception as ex:
                logging.error("receiver error in line %s: %s" % (str(sys.exc_info()[-1].tb_lineno), str(ex)))
        logging.info("end reciever on %s" % self._host)

    @asyncio.coroutine
    def sender(self):
        logging.info("start sender on %s" % self._host)
        while self.connected():
            try:
                message = yield from self._message_queue.get()
                logging.debug("Send: %r" % message)
                message = message + "\n"
                data = message.encode()
                self._writer.write(data)
                yield from self._writer.drain()
            except Exception as ex:
                logging.error("sender error in line %s: %s" % (str(sys.exc_info()[-1].tb_lineno), str(ex)))
        logging.info("end sender on %s" % self._host)

    @asyncio.coroutine
    def pinger(self):
        while self.connected():
            self.ponged = False
            self.append_message({"action": "ping"})
            yield from asyncio.sleep(SOCKET_PING_INTERVAL)
            if not self.ponged:
                logging.error("pong from %s not received in %d seconds, disconnect" % (self._host,
                                                                                       SOCKET_PING_INTERVAL))

    @asyncio.coroutine
    def receive_json(self):
        logging.debug("start receiving")
        data = yield from self._reader.readline()
        message = data.decode()
        if message != '':
            logging.debug("Received %r from %r" % (message, self._host))
            message_object = json.loads(message)
            return message_object
        else:
            self._connected = False
            return False

    def connected(self):
        return self._connected

    def append_message(self, message_object, wait_for_response=False, response_timeout=30.0, action_id=None):
        if action_id is None and "action_id" not in message_object.keys():
            action_id = str(uuid.uuid4())
            message_object["action_id"] = action_id
        result = True
        message = json.dumps(message_object)
        future = asyncio.Future(loop=self._loop)
        if wait_for_response:
            self.wait_responses[message_object["action_id"]] = future
        self._message_queue.put_nowait(message)
        if wait_for_response:
            time_passed = 0.0
            while not future.done():
                time.sleep(0.1)
                time_passed += 0.1
                if time_passed > response_timeout:
                    future.cancel()
                    self.wait_responses.pop(message_object["action_id"])
            if future.cancelled():
                #TODO: возможно выбросить эксепшн
                result = False
            else:
                result = future.result()
        logging.debug("message appended")
        return result

    def save_all_messages(self):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(path + '/../storage/queries_%s.txt' % self._host, "a") as queries_file:
            while self._message_queue.qsize() > 0:
                message = yield from self._message_queue.get()
                queries_file.write("%s\n" % message)

    def load_saved_messages(self):
        path = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(path + '/../storage/queries_%s.txt' % self._host):
            with open(path + '/../storage/queries_%s.txt' % self._host, "r") as queries_file:
                messages = queries_file.read()
                messages = messages.split('\n')
                for message in messages:
                    if message:
                        self._message_queue.put_nowait(message)
        # Truncate queries file
        open(path + '/../storage/queries_%s.txt' % self._host, 'w').close()

    def disconnect(self):
        self._connected = False