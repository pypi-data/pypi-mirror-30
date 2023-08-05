#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-12-04
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from worker.ftp_client import FTPClient
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
from threading import Thread
from unittest import TestCase
import _thread
import os
import sys
import time
import shutil

cliiii = None
client = None
server = None


class TestFTPClient(TestCase, Thread):
    def setup_class(self):
        # init data
        if os.path.isdir("./tmp"):
            shutil.rmtree("./tmp")
        os.mkdir("./tmp")
        os.mkdir("./tmp/dir0")
        open("./tmp/file0", "w").close()
        f = open("./tmp/dir0/file0", "w")
        f.write("123456")
        f.close()
        # init client and server
        global cliiii
        global client
        global server
        # init client
        client = FTPClient("localhost", 21, 1, "root", "root", 1024)
        cliiii = FTPClient("localhost", 21, 1, "hyb", "hyb", 1024)
        # init server
        auth = DummyAuthorizer()
        auth.add_user("root", "root", "./tmp", perm="elradfmwMT")
        auth.add_user("hyb", "hyb", "./tmp", perm="elr")
        handler = FTPHandler
        handler.authorizer = auth
        server = ThreadedFTPServer(("localhost", 21), handler)
        _thread.start_new_thread(server.serve_forever, ())
        time.sleep(0.001)

    def teardown_class(self):
        server.close_all()

    def test_file_info(self):
        # root user
        assert client.isexist("")
        assert client.isdir("")
        assert not client.isfile("")
        assert not client.isexist("1/2/3")
        assert not client.isdir("1/2/3")
        assert not client.isfile("1/2/3")
        assert client.isexist("dir0")
        assert client.isexist("file0")
        assert client.isexist("dir0/file0")
        assert client.isdir("dir0")
        assert client.isfile("file0")
        assert client.isfile("dir0/file0")
        # hyb user
        assert cliiii.isexist("/dir0/")
        assert cliiii.isfile("/dir0/file0")
        assert cliiii.isdir("/")

    def test_mkdir(self):
        # root user
        assert not client.isdir("dir1")
        assert not client.isdir("/dir2/")
        client.mkdir("dir1")
        client.mkdir("/dir2/")
        assert client.isdir("/dir1/")
        assert client.isdir("dir2")
        # mkdir if exists
        self.assertRaises(FileExistsError, client.mkdir, "dir2/")
        # hyb user
        self.assertRaises(PermissionError, cliiii.mkdir, "dir3/")

    def test_mkdir_if_exist(self):
        # root user
        assert not client.isdir("dir4")
        client.mkdir("/dir4/")
        assert client.isdir("dir4")
        client.mkdir_if_not_exist("dir4")
        assert client.isdir("dir4")
        # hyb user
        cliiii.mkdir_if_not_exist("dir4/")

    def test_upload(self):
        # root user
        assert not client.isexist("dir0/test_upload")
        fd = open(__file__, "rb")
        client.upload(fd, "dir0", "test_upload")
        fd.close()
        assert client.isexist("dir0/test_upload")
        # hyb user

    def test_download(self):
        # root user
        fd = open("./tmp/test_download", "wb")
        client.download(fd, "dir0", "file0")
        fd.close()
        assert os.path.isfile("./tmp/test_download")
        # hyb user
