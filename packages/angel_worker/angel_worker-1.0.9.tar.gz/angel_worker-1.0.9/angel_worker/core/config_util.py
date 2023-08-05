#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-27
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

import configparser
import os


def parse(filepath, section):
    if not os.path.isfile(filepath):
        raise Exception("file '%s' not exist" % filepath)
    parser = configparser.ConfigParser()
    parser.read(filepath)
    lists = parser.items(section)
    config = {}
    for ll in lists:
        if len(ll) != 2:
            raise Exception('the configuration of %s is illegal : %s' % (filepath, str(ll)))
        config[ll[0]] = ll[1]
    return config
