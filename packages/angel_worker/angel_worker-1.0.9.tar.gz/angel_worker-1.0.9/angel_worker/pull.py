#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2018-01-12
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

import time
import os
import signal
from threading import Thread
from traceback import format_exc

CAMMAND = "cmd"
TASKS = "tasks"
LOGS = "logs"

class Puller(Thread):
    """
    A looper thread for pulling commands from master
    """

    def __init__(self, logger, rpc_service, pull_time, executor, logcollector):
        super(Puller, self).__init__()
        self.logger = logger
        self.rpc_service = rpc_service
        self.pull_time = pull_time
        self.executor = executor
        self.logcollector = logcollector
        self.started = False

    def run(self):
        """
        Main loop of the pulling thread
        """
        self.started = True
        while self.started:
            # sleep for a while
            time.sleep(self.pull_time)
            # obtain command from master
            try:
                resp = self.rpc_service.pull()
                if resp.success():
                    if resp.content:
                        self.logger.debug(resp.content)
                    cmd = resp.content.get(CAMMAND)
                    tasks = resp.content.get(TASKS)
                    logs = resp.content.get(LOGS)
                else:
                    self.logger.warn("pull fail caused by %s" % resp.content)
                    continue
            except Exception as e:
                self.logger.warn(format_exc())
                continue
            if cmd == 'shutdown':
                os.kill(os.getpid(), signal.SIGTERM)
                return
            try:
                if tasks:
                    self.executor.submit(tasks)
                if logs:
                    for logid in logs:
                        self.logcollector.add_log(logid, str(logid))
            except:
                self.logger.error(format_exc())

        def stop(self):
            """
            Stop the puller
            """
            self.started = False

