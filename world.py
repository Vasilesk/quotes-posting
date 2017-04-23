#!/usr/bin/python3
# -*- coding: utf8 -*-

from requests import Request_generator
from schedule import Scheduler
from viewer import Viewer
from PyQt5.QtWidgets import QApplication
import sys

class World:
    def __init__(self, cursor):
        self.cursor = cursor


    def run(self, posting_interval, request_interval, coefs):
        self.request_generator = Request_generator(request_interval, self.cursor)
        self.scheduler = Scheduler(posting_interval, coefs, self.cursor)

        app = QApplication(sys.argv)
        self.viewer = Viewer(self.cursor, posting_interval, request_interval, coefs)

        self.request_generator.new_request_signal.connect(self.viewer.on_request)
        self.request_generator.new_request_signal.connect(self.scheduler.on_request)
        self.scheduler.new_post_signal.connect(self.viewer.on_post)

        self.viewer.posting_state_signal.connect(self.scheduler.on_posting_state)
        self.viewer.requesting_state_signal.connect(self.request_generator.on_requesting_state)

        self.viewer.posting_interval_signal.connect(self.scheduler.on_interval_change)
        self.viewer.requesting_interval_signal.connect(self.request_generator.on_interval_change)

        self.viewer.change_coef_signal.connect(self.scheduler.on_coef_change)

        self.request_generator.start()
        self.scheduler.start()
        sys.exit(app.exec_())
