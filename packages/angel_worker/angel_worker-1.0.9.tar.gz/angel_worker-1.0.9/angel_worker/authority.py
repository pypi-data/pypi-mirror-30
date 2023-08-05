#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-21
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

import hashlib
import os
import sys


class Authority(object):
    """
    Helper class for register, login and logout
    """
    def __init__(self, rpc_client, auth_path, desc, logger=None):
        self.rpc_client = rpc_client
        self.auth_path = auth_path
        self.desc = desc
        self.logger = logger

    def register(self, name, password, force=False):
        """
        Send a register request to master with 'name' and 'password'
        External command for shell, not deamon
        """
        if not force and os.path.isfile(self.auth_path):
            raise Exception("already register")
        # mkdir if not exist
        dirname = os.path.dirname(self.auth_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
            os.chmod(dirname, mode=0o777)
        # to store key(worker_id, name, password)
        with open(self.auth_path, "w") as f:
            # obtain the hash of name
            _name = hashlib.sha1(name.encode("utf8")).hexdigest()
            # obtain the hash of password
            _password = hashlib.sha1(password.encode("utf8")).hexdigest()
            # register by rpc client
            params = {}
            if self.desc:
                params["desc"] = self.desc
            resp = self.rpc_client.register(_name, _password, params)
            # check if login successfully
            if resp.success():
                worker_id = resp.content
                # store key(worker_id, name, password) after register
                f.write(str(worker_id))
                f.write("\n")
                f.write(_name)
                f.write("\n")
                f.write(_password)
                sys.stdout.write("register successfully, author file : %s\n" % self.auth_path)
            else:
                raise Exception(resp.content)

    def login(self):
        """
        Send a login request to master
        Return worker_id if login successfully
        """
        # check if the auth file exist
        if not os.path.isfile(self.auth_path):
            # no auth file, not register before
            message = "login fail, not register before login"
            self.logger.warn(message)
            raise Exception(message)
        with open(self.auth_path, "r") as f:
            # read auth file, get the hash of name and password
            key = f.read()
            keys = key.split("\n")
            if len(keys) != 3:
                self.logger.error("something wrong with the key in %s" % self.auth_path)
            try:
                # login by rpc client
                resp = self.rpc_client.login(keys[1], keys[2], int(keys[0]))
                if resp.success():
                    self.logger.info("login successfully")
                    self.rpc_client.worker_id = int(keys[0])
                else:
                    message = "login fail, Master: %s" % resp.content
                    self.logger.warn(message)
                    raise Exception (message)
            except Exception as e:
                message = "login fail caused by %s" % str(e)
                self.logger.warn(message)
                raise Exception(message)

    def logout(self):
        """
        Send a logout request to master
        """
        try:
            resp = self.rpc_client.logout()
            if resp.success():
                self.logger.info("logout successfully")
                return
            else:
                message = "logout fail, Master: %s" % resp.content
        except Exception as e:
            message = "logout fail, caused by %s" % str(e)
        raise Exception(message)

