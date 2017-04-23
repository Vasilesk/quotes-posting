#!/usr/bin/python3
# -*- coding: utf8 -*-

# Tunnel Config
SSH_HOST = "mysite.ru"
SSH_USER = "user"
SSH_KEYFILE = "key.pem"
SSH_FOREIGN_PORT = 5432   # Port that postgres is running on the foreign server
SSH_INTERNAL_PORT = 5434  # Port we open locally that is forwarded to
                          # FOREIGN_PORT on the server.

command = "ssh -i %s %s@%s -fNL %d:localhost:%d"\
    % (SSH_KEYFILE, SSH_USER, SSH_HOST, SSH_INTERNAL_PORT, SSH_FOREIGN_PORT)
