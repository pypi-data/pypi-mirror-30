#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2018-01-10
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

import os
import sys
import getpass
from angel_worker.authority import Authority
from angel_worker.core import config_util
from angel_worker.api.rpc_service import RPCService

ETC_PATH = "/etc/angel/worker"


def main():
    # loading configurations
    config_path = os.path.join(ETC_PATH, "worker.conf")
    config = config_util.parse(config_path, "worker")
    auth_path = config["auth_path"]
    desc = config["description"]
    rpc_url = config["rpc_url"]
    rpc_client = RPCService(None, rpc_url)
    auth = Authority(rpc_client, auth_path, desc)
    sys.stdout.write("Please input admin username:")
    sys.stdout.flush()
    # obtain name and password from command line
    name = str.strip(sys.stdin.readline())
    password = str.strip(getpass.getpass("Please input admin password:"))
    # check if register by force
    if "-f" in sys.argv:
        auth.register(name, password, force=True)
    else:
        auth.register(name, password)

if __name__ == "__main__":
    main()
