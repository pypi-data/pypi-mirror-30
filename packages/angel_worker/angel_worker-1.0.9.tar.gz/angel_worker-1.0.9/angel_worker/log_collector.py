#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-12-07
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_worker.core.tail import Tail
from threading import Thread, current_thread
from traceback import format_exc
import requests
import json
import os


class LogCollector(Thread):
    """
    Collecting real-time log and send to the LogMonitor
    """

    def __init__(self, logger, url, dirpath, loop_time=1, last_bytes=1024):
        self.logger = logger
        self.url = url
        self.dirpath = dirpath
        self.loop_time = loop_time
        self.last_bytes = last_bytes
        self.tails = {}

    def add_log(self, task_id, filename):
        """
        Add a new log file to monitor in real-time
        """
        # check if already exist
        if task_id in self.tails:
            return
        filepath = os.path.join(self.dirpath, filename)
        # check if log file exist
        if not os.path.isfile(filepath):
            return
        tail = Tail(filepath, self.loop_time, self.last_bytes)
        tail.register_callback(self._send_log)
        self.tails[task_id] = tail
        thread = Thread(name="tasklog(%s)" % task_id)
        thread.run = tail.serve
        thread.task_id = task_id
        thread.tail = tail
        thread.start()

    def stop_logger(self, task_id=None):
        """
        Stop all log tailer
        """
        if task_id is not None:
            tail = self.tails.get(task_id)
            if tail is not None:
                tail.stop_serve()
                del self.tails[task_id]
            return
        for tail in self.tails.values():
            tail.stop_serve()
        self.tails.clear()

    def _send_log(self, log):
        """
        Helper method to send log and handle the response
        """
        task_id = current_thread().task_id
        tail = current_thread().tail
        data = {"task_id": task_id, "log": log}
        try:
            resp = requests.post(self.url, data=data)
            content = str(resp.content, encoding="utf-8")
            res = json.loads(content)
            if res.get("statusCode") != 200:
                tail.stop_serve()
                del self.tails[task_id]
        except:
            tail.stop_serve()
            del self.tails[task_id]
            self.logger.warn("send log to logmonitor fail caused by " + format_exc())

