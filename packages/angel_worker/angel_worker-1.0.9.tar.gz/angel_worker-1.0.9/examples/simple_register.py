#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2018-01-13
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


if __name__ == "__main__":
    from angel_worker.authority import Authority
    from angel_worker.core import config_util
    from angel_worker.api.rpc_service import RPCService
    import os
    config_path = os.path.join("/etc/angel/worker", "worker.conf")
    config = config_util.parse(config_path, "worker")
    auth_path = config["auth_path"]
    desc = config["description"]
    rpc_url = config["rpc_url"]
    rpc_client = RPCService(None, rpc_url)
    auth = Authority(rpc_client, auth_path, desc)
    name = "root"
    password = "root"
    auth.register(name, password)
