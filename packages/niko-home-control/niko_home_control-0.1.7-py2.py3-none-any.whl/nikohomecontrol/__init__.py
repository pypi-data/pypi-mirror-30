#!/usr/bin/env python3

'''
.. module:: nikohomecontrol
    :platform: Unix, Windows
    :synopsis: Python API to interact with Niko Home Control
    :noindex:
'''

import socket
import json
import time
from io import StringIO

class Hub:
    def __init__(self, config):
        self._config = config
        self._connect()

    def _connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._config['ip'], self._config['port']))

    def __del__(self):
        self._socket.shutdown(1)
        self._socket.close()

    def system_info_raw(self):
        return self._command('{"cmd":"systeminfo"}')

    def list_actions_raw(self):
        return self._command('{"cmd":"listactions"}')

    def list_actions(self):
        return [Action(action, self) for action in self.list_actions_raw()]

    def list_energy_raw(self):
        return self._command('{"cmd":"listenergy"}')

    def list_locations_raw(self):
        return self._command('{"cmd":"listlocations"}')

    def list_locations(self):
        return [Location(location) for location in self.list_locations_raw()]

    def execute_actions(self, id, value):
        return self._command('{"cmd": "executeactions", "id": '+str(id)+', "value1": '+str(value)+'}')

    def _command(self, cmd, delay=1):
        try:
            self._socket.send(cmd.encode())
            data = json.load(StringIO(self._socket.recv(4096).decode()))
        except BrokenPipeError:
            time.sleep(delay)
            delay = delay * 2
            self._connect()
            return self._command(cmd, delay)

        if ('error' in data['data'] and data['data']['error'] > 0):
            error = data['data']['error']
            print(cmd)
            print(data)
            if (error == 100):
                raise Error('NOT_FOUND')
            if (error == 200):
                raise Error('SYNTAX_ERROR')
            if (error == 300):
                raise Error('ERROR')

        return data['data']

class Location:
    def __init__(self, location):
        self._state = location

    @property
    def id(self):
        return self._state['id']

    @property
    def name(self):
        return self._state['name']

class Action:
    def __init__(self, action, hub):
        self._id = action['id']
        self._state = action
        self._hub = hub

    @property
    def name(self):
        return self._state['name']

    @property
    def id(self):
        return self._state['id']

    @property
    def is_on(self):
        return self._state['value1'] != 0

    def turn_on(self, brightness=255):
        return self._hub.execute_actions(self._id, brightness)

    def turn_off(self):
        return self._hub.execute_actions(self._id, 0)

    def toggle(self):
        if (self.is_on):
            return self.turn_off()
        else:
            return self.turn_on()

    def update(self):
        self._state = next(filter(lambda a: a['id'] == self._id, self._hub.list_actions_raw()))


