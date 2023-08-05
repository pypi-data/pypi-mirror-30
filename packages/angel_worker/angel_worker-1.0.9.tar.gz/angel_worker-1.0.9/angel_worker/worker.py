#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-18
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_worker.core import config_util
from angel_worker.executor import Executor
from angel_worker.authority import Authority
from angel_worker.heartbeat import Heartbeat
from angel_worker.pull import Puller
from angel_worker.api.rpc_service import RPCService
from angel_worker.core.ftp_client import FTPClient
from angel_worker.log_collector import LogCollector
from logging import config
from threading import Thread
from traceback import format_exc
import os
import logging
import time
import signal

ETC_PATH = '/etc/angel/worker/'

executor = None
puller = None
logcollector = None
heartbeat = None
logger = None
client = None
rpc_service = None

def _start():
    """
    Start up the worker service
    """
    heartbeat.start()
    puller.start()

def _on_terminated(*args):
    """
    Stop the worker service
    """
    try:
        heartbeat.stop()
        executor.clean_tasks()
        logcollector.stop_logger()
        authority.logout()
    except:
        self.logger.error(format_exc())
    os.kill(os.getpid(), signal.SIGKILL)


def _on_task_finish(task_id, state):
    """
    Callback when a task finished(success or fail)
    """
    logcollector.stop_logger(task_id)
    heartbeat.running_tasks = executor.running_tasks

def serve_forever(debug=False):
    global rpc_service
    global logger
    global client
    global executor
    global puller
    global logcollector
    global heartbeat
    # setup logger
    logger_config_path = os.path.join(ETC_PATH, "logger.conf")
    logging.config.fileConfig(logger_config_path)
    if debug:
        logger = logging.getLogger("debug")
    else:
        logger = logging.getLogger("release")
    # load setting
    config_path = os.path.join(ETC_PATH, "worker.conf")
    try:
        config = config_util.parse(config_path, "worker")
        pull_time = int(config["pull_time"])
        process_refresh_time = int(config["process_refresh_time"])
        max_tasks = int(config["max_tasks"])
        script_path = config["local_script_path"]
        log_path = config["local_log_path"]
        heartbeat_time = int(config["heartbeat_time"])
        auth_path = config["auth_path"]
        fs_host = config["fs_host"]
        fs_port = int(config["fs_port"])
        fs_timeout = int(config["fs_timeout"])
        fs_name = config["fs_name"]
        fs_pwd = config["fs_password"]
        fs_buffer_size = int(config["fs_buffer_size"])
        fs_script_path = config["fs_script_path"]
        fs_log_path = config["fs_log_path"]
        log_url = config["log_url"]
        desc = config.get("description")
        ha = config["ha"].lower() == "true"
        if ha:
            # start worker in ha mode
            etcd_urls = config["etcd_urls"].split(",")
            namespace = config["namespace"]
            import etcd3ctl
            client = etcd3ctl.Client(namespace, _on_resume, _on_pause, urls=etcd_urls)
            client.setup_etcd_server()
            rpc_url = client.get_current_service_url()
            client.watch_callback_async()
        else:
            rpc_url = config["rpc_url"]
    except Exception as e:
        logger.error("config file '%s' error: %s" % (config_path, str(e)))
        raise
    # create directorys
    if not os.path.isdir(script_path):
        os.makedirs(script_path)
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    # init rpc client
    rpc_service = RPCService(logger, rpc_url)
    # init filesystem client
    fs_client = FTPClient(fs_host, fs_port, fs_timeout, fs_name, fs_pwd, fs_buffer_size)
    # init authority
    authority = Authority(rpc_service, auth_path, desc, logger)
    # init executor
    executor = Executor(rpc_service, logger, process_refresh_time, max_tasks,
                             script_path, log_path, fs_client, fs_script_path, fs_log_path)
    executor.set_task_listener(_on_task_finish)
    # init heartbeat
    heartbeat = Heartbeat(rpc_service, logger, heartbeat_time)
    # init logcollector
    logcollector = LogCollector(logger, log_url, log_path)
    # init puller
    puller = Puller(logger, rpc_service, pull_time, executor, logcollector)
    # register function to catch SIGTERM signal
    signal.signal(signal.SIGTERM, _on_terminated)
    # login
    authority.login()
    # start services
    _start()

def _on_resume():
    master_url = client.get_current_service_url()
    logger.info("Master service started:" + master_url)
    rpc_service.set_master_url(master_url)

def _on_pause():
    logger.info("Master service stopped")

