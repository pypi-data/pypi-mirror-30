"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from threading import Thread
import socket
import json
import struct
import logging
import sys
from time import sleep
from common import JemuConnectionException


class JemuConnection:
    _addr = None
    _conn = None
    _HANDSHAKE = "handshake"
    _COMMAND = "command"
    _COMMAND_TYPE = "command_type"
    _PERIPHERAL_ID = "peripheral_id"
    _TRANSITION_TYPE = "transition_type"
    _PIN_NUM = "pin_number"
    _MESSAGE_ID = "message_id"
    _VOLTAGE = "voltage"
    _API_VERSION = "1"
    _OK = "ok"
    _ERROR = "error"
    _ERROR_CODE = "404"
    _TYPE = "type"
    _RESPONSE = "response"
    _API_V_STRING = "api_version"
    _ERROR_MESSAGE = "error"
    _COMMAND_START = "start"
    _NANO_SECONDS = "nanoseconds"

    _LOG_LEVEL = logging.ERROR
    _logger = logging.getLogger()
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    _logger.addHandler(log_handler)
    _logger.setLevel(_LOG_LEVEL)
    log_handler.setLevel(_LOG_LEVEL)

    def __init__(self, addr):
        self._addr = addr
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._conn.settimeout(0.3)
        self._callbacks = []
        self._thread = None
        self._should_run = False
        self._connection_closed = True
        self._threads = []

    def start(self):
        self._should_run = True
        t = Thread(target=self.connection_task)
        self._threads.append(t)
        t.start()

    def close(self):
        self._should_run = False
        for t in self._threads:
            t.join()

    def is_connected(self):
        return self._should_run

    def connection_task(self):
        while self._should_run:
            json_buff_string = self.recv_json()
            if json_buff_string is None:
                self._should_run = False
                break
            self._logger.debug("received data: " + json_buff_string)
            json_pack = json.loads(json_buff_string)
            t = Thread(target=self.inform, args=(json_pack,))
            self._threads.append(t)
            t.start()
            if len(self._threads) > 4:
                self.clean_threat_list()

        if not self._connection_closed:
            self._conn.close()
            self._connection_closed = True

    def inform(self, jemu_json_packet):
        for callback in self._callbacks:
            callback(jemu_json_packet)

    def register(self, callback):
        self._callbacks.append(callback)

    def connect(self, port):
        result = False
        try:
            self._conn.connect((self._addr, int(port)))
            self._connection_closed = False
            result = True
        except Exception:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        finally:
            return result

    def handshake(self, ns=None):
        self._should_run = True
        self.send_handshake()
        response_ack = self.recv_json()
        if response_ack is None:
            return False
        self.check_response(response_ack)
        self.send_start(ns)
        return True

    def check_response(self,response_ack):
        self._logger.debug("handshake response data: " + response_ack)
        response = json.loads(response_ack)
        message_type = response[self._TYPE]
        if message_type != self._RESPONSE:
            self._should_run = False
            raise JemuConnectionException("Error expect response message instead got [" + message_type + "]")
        status_code = response[self._RESPONSE]
        if status_code != self._OK:
            self._should_run = False
            raise JemuConnectionException("Sdk's api version does not match to the jemu's version")

    def send_json(self, json_obj):
        data_to_send = json.dumps(json_obj)
        number_of_bytes = len(data_to_send.encode('utf-8'))
        self._logger.debug("Number of byte of send data: " + str(number_of_bytes))
        number_to_send = struct.pack('!i', number_of_bytes)
        self.send(number_to_send)
        self._logger.debug("Data to send: " + data_to_send)
        self.send(data_to_send)

    def send_handshake(self):
        hand_shake_message = {self._API_V_STRING: self._API_VERSION, self._TYPE: self._HANDSHAKE}
        self.send_json(hand_shake_message)

    def send_start(self, ns=None):
        ack = {self._TYPE: self._COMMAND, self._COMMAND: self._COMMAND_START}
        if ns:
            ack[self._NANO_SECONDS] = ns
        self.send_json(ack)

    def send(self, buffer):
        try:
            self._conn.sendall(buffer)
        except socket.error as e:
            self._should_run = False
            raise JemuConnectionException("Jemu connection failed with error: " + str(e))

    def clean_threat_list(self):
        for t in self._threads:
            if not t.isAlive():
                self._threads.remove(t)

    def recv_json(self):
        data = self.receive(4)
        if data is None:
            return None
        buffer_size = struct.unpack("!i", data)[0]
        self._logger.debug("Number of byte of received data: " + str(buffer_size))
        if buffer_size == 0:
            return None
        data = self.receive(buffer_size)
        if data is None:
            return None
        else:
            return data

    def receive(self, size):
        result = b''
        while (len(result) < size) and (not self._connection_closed):
            if not self._should_run:
                return None

            try:
                data = self._conn.recv(size - len(result))
            except socket.timeout:
                continue
            except socket.error as e:
                sleep(0.2)
                if self._should_run:
                    self._should_run = False
                    raise JemuConnectionException("Jemu connection failed with error: " + str(e))
                else:
                    self._connection_closed = True
                    return None

            if data == b'':
                self._connection_closed = True
                return None
            else:
                result += data

        return result