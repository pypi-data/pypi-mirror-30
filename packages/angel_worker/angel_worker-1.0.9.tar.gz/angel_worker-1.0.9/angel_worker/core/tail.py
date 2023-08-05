#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-12-06
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

import time
import os
import sys
from threading import Thread


class Tail(object):
    """
    Represents 'tail' command in unix
    Used to monitor log file
    """

    def __init__(self, filepath, loop_time, last_bytes):
        super(Tail, self).__init__()
        self.filepath = filepath
        self.loop_time = loop_time
        self.last_bytes = last_bytes
        self.callback = sys.stdout.write
        self.started = False

    def serve(self):
        """
        Monitor the file
        Callback begin with the last part of the file(last bytes),
        continue with every new lines
        """
        self.started = True
        filesize = os.path.getsize(self.filepath)
        with open(self.filepath, "r") as fd:
            # seek to the last part of the file
            if filesize > self.last_bytes:
                fd.seek(filesize - self.last_bytes, os.SEEK_SET)
            # read the end lines of the file
            while self.started:
                lines = fd.readlines()
                if lines:
                    self._handle_lines(lines)
                else:
                    time.sleep(self.loop_time)

    def _handle_lines(self, lines):
        """
        Callback when new lines received
        """
        # conbine mulit lines into a message
        if not lines:
            return
        if len(lines) == 1:
            result = lines[0]
        elif len(lines) > 1:
            result = ""
            for line in lines:
                result += line
        # callback with new lines
        if self.callback:
            self.callback(result)

    def register_callback(self, callback):
        """
        Set callback function
        """
        self.callback = callback

    def stop_serve(self):
        """
        Stop the Tail
        """
        self.started = False
