#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-18
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from collections import namedtuple
from concurrent.futures.thread import ThreadPoolExecutor
from angel_worker import constants
from traceback import format_exc
import os, stat, subprocess, time

Task = namedtuple("Task", "id job_id state")



class Executor(object):
    """
    A executor that execute the tasks obtained from master
    """

    def __init__(self, rpc_client, logger, process_refresh_time, max_tasks,
                 script_path, log_path, fs_client, fs_script_path, fs_log_path):
        self.started = False
        self.rpc_client = rpc_client
        self.logger = logger
        self.process_refresh_time = process_refresh_time
        self.thread_pool = ThreadPoolExecutor(max_tasks)
        self.script_path = script_path
        self.log_path = log_path
        self.fs_client = fs_client
        self.fs_script_path = fs_script_path
        self.fs_log_path = fs_log_path
        self.processes = {}
        self.running_tasks = 0
        self.task_listener = None
        # create logs and scripts directory
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        if not os.path.isdir(script_path):
            os.mkdir(script_path)

    def clean_tasks(self):
        """
        Stop all tasks
        """
        for process in self.processes.values():
            process.kill()

    def set_task_listener(self, listener):
        """
        setup a listener for changing state of tasks
        """
        self.task_listener = listener

    def submit(self, tasks):
        """
        Submit tasks to executor
        """
        for item in tasks:
            task = Task(**item)
            if task.state == constants.STATE_RUNNING_TIMEOUT:
                # stop the running timeout tasks
                process = self.processes.get(task.id)
                if process:
                    process.kill()
            else:
                # new processes to execute tasks
                self.thread_pool.submit(self._run_task, task)

    def _run_task(self, task):
        """
        run the task in the new process
        """
        # download the script if not exist in local file system
        path = os.path.join(self.script_path, "%d" % task.job_id)
        try:
            # download from file system
            with open(path, "wb") as fd:
                self.fs_client.download(fd, self.fs_script_path, str(task.job_id))
        except Exception as e:
            os.remove(path)
            self.logger.warn("download scipt file fail caused by %s" % str(e))
            try:
                self.rpc_client.task_callback(task.id, constants.STATE_DOWNLOAD_FAIL)
            except Exception as e:
                self.logger.warn("task callback fail caused by %s" % str(e))
            return
        # add exec flag
        os.chmod(path, stat.S_IRWXU)
        # open files to store the logs of the process
        with open(os.path.join(self.log_path, str(task.id)), "w") as f:
            self.running_tasks = self.running_tasks + 1
            # fork a new process to execute the script
            p = subprocess.Popen(path, stdout=f, stderr=f)
            self.processes[task.id] = p
            # check if it is finished
            while p.poll() is None:
                time.sleep(self.process_refresh_time)
        # upload the log
        try:
            with open(os.path.join(self.log_path, "%d" % task.id), "rb") as f:
                self.fs_client.upload(f, self.fs_log_path, str(task.id))
        except Exception as e:
            self.logger.error(format_exc())
        # remove the process
        del self.processes[task.id]
        # callback the master that the task is finished(success or fail)
        returncode = p.poll()
        self.running_tasks = self.running_tasks - 1
        if returncode == 0:
            state = constants.STATE_SUCCESS
        elif returncode == -9:
            state = constants.STATE_RUNNING_TIMEOUT
        else:
            state = constants.STATE_FAIL
        if self.task_listener:
            self.task_listener(task.id, state)
        try:
            self.rpc_client.task_callback(task.id, state)
        except Exception as e:
            pass
