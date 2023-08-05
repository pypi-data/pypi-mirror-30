#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-21
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_worker.api.response import ResponseMessage
from xmlrpc.client import ServerProxy
from traceback import format_exc
import time
from http.client import CannotSendRequest

task_callbacks = []
CALLBACK_MAX_SIZE = 1024


def exception_handler(func):
    """
    Handle exception and package the response
    """
    def wrapper(self, *args, **kwargs):
        try:
            resp = func(self, *args, **kwargs)
            return ResponseMessage(resp.get("code"), resp.get("content"))
        except Exception as e:
            self.logger.warn("%s rpc fail caused by %s" % (func.__name__, format_exc()))
            raise
    return wrapper


class RPCService(object):
    """
    RPC Client that call the service of master
    """

    def __init__(self, logger, url):
        self.url = url
        self.logger = logger
        self.heartbeat_client = ServerProxy(self.url)
        self.pull_client = ServerProxy(self.url)

    def set_master_url(self, master_url):
        self.url =  master_url
        self.heartbeat_client = ServerProxy(self.url)
        self.pull_client = ServerProxy(self.url)

    @exception_handler
    def register(self, name, password, params):
        client = ServerProxy(self.url)
        return client.register(name, password, params)

    @exception_handler
    def login(self, name, password, worker_id):
        client = ServerProxy(self.url)
        return client.login(name, password, worker_id)

    @exception_handler
    def logout(self):
        client = ServerProxy(self.url)
        return client.logout(self.worker_id)

    @exception_handler
    def heartbeat(self, params):
        return self.heartbeat_client.heartbeat(self.worker_id, params)

    #@exception_handler
    #def pull_tasks(self):
    #    if not hasattr(self, "pulltask_client"):
    #        self.pulltask_client = ServerProxy(self.url)
    #    return self.pulltask_client.pull_tasks(self.worker_id)

    @exception_handler
    def pull(self):
        return self.pull_client.pull(self.worker_id)

    def task_callback(self, task_id, state):
        try:
            client = ServerProxy(self.url)
            if len(task_callbacks) > CALLBACK_MAX_SIZE:
                raise Exception("too many callbacks")
            task_callbacks.append((task_id, int(time.time()), self.worker_id, state))
            resp = client.task_callback(task_callbacks)
            resp = ResponseMessage(resp.get("code"), resp.get("content"))
            if resp.success():
                task_callbacks.clear()
                return resp
            else:
                self.logger.warn("task callback fail caused by %s" % resp.content)
        except Exception as e:
            self.logger.warn("task callback fail caused by %s" % format_exc())
            raise
