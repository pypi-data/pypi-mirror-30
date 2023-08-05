#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-21
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

CODE_SUCCESS = 0
CODE_FAIL = 1


class ResponseMessage(object):
    """
    Response message from master when rpc
    """

    def __init__(self, code=CODE_SUCCESS, content=None):
        self.code = code
        self.content = content

    def success(self):
        return self.code == CODE_SUCCESS
