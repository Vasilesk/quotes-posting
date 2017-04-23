#!/usr/bin/python3
# -*- coding: utf8 -*-

from sshtunnel import SSHTunnel
import psycopg2
import json

from world import World

from config.tunnel import command, SSH_INTERNAL_PORT
from config.init_values import coefs, posting_interval, request_interval

SSH_ON = False

if __name__ == '__main__':
    config_filename = 'config/db_over_ssh.json' if SSH_ON else 'config/db.json'
    config_file = open(config_filename, 'r')
    db_config = json.load(config_file)
    config_file.close()
    if SSH_ON:
        with SSHTunnel(command):
            conn = psycopg2.connect(**db_config, port = SSH_INTERNAL_PORT)
            cursor = conn.cursor()

            w = World(cursor)
            w.run(posting_interval, request_interval, coefs)
    else:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        w = World(cursor)
        w.run(posting_interval, request_interval, coefs)
