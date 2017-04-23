#!/usr/bin/python3
# -*- coding: utf8 -*-

# Code from here:
# https://stackoverflow.com/a/26289475

import psutil
import subprocess
import time
import os

class SSHTunnel(object):
    """
    A context manager implementation of an ssh tunnel opened from python

    """
    def __init__(self, tunnel_command):
        assert "-fN" in tunnel_command, "need to open the tunnel with -fN"
        self._tunnel_command = tunnel_command
        self._delay = 0.1
        self.ssh_tunnel = None

    def create_tunnel(self):
        tunnel_cmd = self._tunnel_command
        ssh_process = subprocess.Popen(tunnel_cmd, universal_newlines=True,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE)

        # Assuming that the tunnel command has "-f" and "ExitOnForwardFailure=yes", then the
        # command will return immediately so we can check the return status with a poll().

        while True:
            p = ssh_process.poll()
            if p is not None: break
            time.sleep(self._delay)


        if p == 0:
            # Unfortunately there is no direct way to get the pid of the spawned ssh process, so we'll find it
            # by finding a matching process using psutil.

            current_username = psutil.Process(os.getpid()).username()
            ssh_processes = [proc for proc in psutil.process_iter() if proc.cmdline() == tunnel_cmd.split() and proc.username() == current_username]

            if len(ssh_processes) == 1:
                self.ssh_tunnel = ssh_processes[0]
                return ssh_processes[0]
            else:
                raise RuntimeError('multiple (or zero?) tunnel ssh processes found: ' + str(ssh_processes))
        else:
            raise RuntimeError('Error creating tunnel: ' + str(p) + ' :: ' + str(ssh_process.stdout.readlines()))

    def release(self):
        """ Get rid of the tunnel by killin the pid
        """
        if self.ssh_tunnel:
            self.ssh_tunnel.terminate()

    def __enter__(self):
        self.create_tunnel()
        return self

    def __exit__(self, type, value, traceback):
        self.release()

    def __del__(self):
        self.release()
