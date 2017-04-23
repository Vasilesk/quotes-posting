#!/usr/bin/python3
# -*- coding: utf8 -*-

import random

from time import sleep
from PyQt5.QtCore import QThread, pyqtSignal

class Scheduler(QThread):
    new_post_signal = pyqtSignal(int)
    def __init__(self, inerval, coefs, cursor):
        super().__init__()
        self.interval = inerval
        self.posting_state = True
        self.coefs = coefs

        query = 'SELECT id, author_id, source_id FROM quotes;'
        cursor.execute(query)
        self.candidates = {quote_id: {'author': author_id, 'source': source_id, 'tags' : [], 'p_coef': 0.0} for quote_id, author_id, source_id in cursor.fetchall()}

        query = 'SELECT quote_id, tag_id FROM quotes_tags;'
        cursor.execute(query)
        for quote_id, tag_id in cursor.fetchall():
            self.candidates[quote_id]['tags'].append(tag_id)

        self.candidates = [{'quote': x, **self.candidates[x]} for x in self.candidates]
        random.shuffle(self.candidates)

    def on_request(self, request):
        self.add_request(request)

    def on_posting_state(self, state):
        self.posting_state = state

    def on_interval_change(self, interval):
        self.interval = interval

    def on_coef_change(self, update_dict):
        for key in update_dict:
            self.coefs[key].update(update_dict[key])

    def run(self):
        n = 0
        while True:
            if self.posting_state:
                post = self.get_quote_to_post()
                self.new_post_signal.emit(post)
                n += 1
                sleep(self.interval)

    def add_request(self, request):
        candidates = []
        for candidate in self.candidates:
            for request_type in request:
                if request_type == 'tag':
                    if request[request_type] in candidate['tags']:
                        candidate['p_coef'] += self.coefs['inc'][request_type]
                    else:
                        candidate['p_coef'] += 1.0
                elif request_type in ('author', 'source'):
                    if candidate[request_type] == request[request_type]:
                        candidate['p_coef'] += self.coefs['inc'][request_type]
                    else:
                        candidate['p_coef'] += 1.0
                elif request_type == 'quote' and candidate[request_type] == request[request_type]:
                    candidate['p_coef'] += self.coefs['inc'][request_type]
                else:
                    candidate['p_coef'] += 1.0
            candidates.append(candidate)
        self.candidates = candidates

    def fullfill_request(self, chosen):
        for candidate in self.candidates:
            for chosen_feature in ('author', 'source'):
                if chosen[chosen_feature] is not None and candidate[chosen_feature] == chosen[chosen_feature]:
                    candidate['p_coef'] -= self.coefs['dec'][chosen_feature]

            if candidate['quote'] == chosen['quote']:
                candidate['p_coef'] -= self.coefs['dec']['quote']

            for chosen_tag in chosen['tags']:
                for candidate_tag in candidate['tags']:
                    if chosen_tag == candidate_tag:
                        candidate['p_coef'] -= self.coefs['dec']['tag'] / len(candidate['tags'])

    def get_quote_to_post(self):
        self.candidates = sorted(self.candidates, key=lambda k: k['p_coef'], reverse=True)
        chosen = self.candidates[0]
        self.fullfill_request(chosen)
        return chosen['quote']
