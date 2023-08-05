#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-18
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from threading import Thread
import psutil
import time
import os
import signal


class Heartbeat(Thread):
    """
    A heartbeat thread that get its performance and sent to the master
    """
    def __init__(self, rpc_client, logger, heartbeat_time):
        super(Heartbeat, self).__init__()
        self.started = False
        self.heartbeat_time = heartbeat_time
        self.rpc_client = rpc_client
        self.logger = logger
        self.running_tasks = 0

    def start(self):
        """
        start up the heartbeat thread
        """
        self.started = True
        super(Heartbeat, self).start()

    def stop(self):
        """
        stop the heartbeat thread
        """
        self.started = False

    def run(self):
        """
        Main loop of the heartbeat thread
        """
        performances = {}
        while self.started:
            # sleep for a while
            time.sleep(self.heartbeat_time)
            # get its performance parameters
            cpu_free = 100 - psutil.cpu_percent()
            mem_total = psutil.virtual_memory().total
            mem_avai = psutil.virtual_memory().available
            mem_free = mem_avai * 100 / mem_total
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            performances["cpu_free"] = float('%.2f' % cpu_free)
            performances["memory_free"] = float('%.2f'% mem_free)
            performances["disk_write"] = disk_io.write_count
            performances["disk_read"] = disk_io.read_count
            performances["net_send"] = net_io.packets_sent
            performances["net_rev"] = net_io.packets_recv
            performances["running_tasks"] = self.running_tasks
            # send to the master
            try:
                resp = self.rpc_client.heartbeat(performances)
                if not resp.success():
                    self.logger.warn("heartbeat error caused by:" % resp.content)
                    os.kill(os.getpid(), signal.SIGTERM)
            except:
                pass
