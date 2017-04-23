#!/usr/bin/python3
# -*- coding: utf8 -*-

import random

from time import sleep
from PyQt5.QtCore import QThread, pyqtSignal

class Request_generator(QThread):
    new_request_signal = pyqtSignal(dict)
    def __init__(self, inerval, cursor):
        super().__init__()
        self.interval = inerval
        self.requesting_state = True
        tables = {'quote':'quotes', 'author':'authors', 'source':'sources', 'tag':'tags'}
        self.data_keys = ('quote', 'author', 'source', 'tag')
        self.data = dict()
        for key in self.data_keys:
            query = 'SELECT id FROM {};'.format(tables[key])
            cursor.execute(query)
            self.data[key] = [x[0] for x in cursor.fetchall()]

    def run(self):
        n = 0
        while True:
            if self.requesting_state:
                request = self.get_request()
                self.new_request_signal.emit(request)
                n += 1
                sleep(self.interval)

    def get_request(self):
        request_type = self.rand_data_key()
        request_value = self.rand_data_element_by_key(request_type)
        return {request_type: request_value}

    def rand_data_key(self):
        return self.data_keys[random.randint(0, len(self.data_keys) - 1)]

    def rand_data_element_by_key(self, data_key):
        return self.data[data_key][random.randint(0, len(self.data[data_key]) - 1)]

    def on_requesting_state(self, state):
        self.requesting_state = state

    def on_interval_change(self, interval):
        self.interval = interval
