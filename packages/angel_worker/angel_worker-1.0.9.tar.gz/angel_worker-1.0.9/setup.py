#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2018-01-10
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


from setuptools import setup, find_packages
import sys
import os

ETC_PATH = "/etc/angel/worker/"

setup(
    name="angel_worker",
    version="1.0.9",
    author="Lafite93",
    author_email="2273337844@qq.com",
    description="The worker of a distribute job scheduler named 'angel'",
    license="Apache",
    keywords="angel worker executor",
    url="https://pypi.python.org/pypi/angel_worker",
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        (ETC_PATH, ['etc/worker.conf', 'etc/logger.conf'])
    ],
    scripts=["scripts/worker_daemon", "scripts/register_worker"],
    install_requires=[
        "configparser",
        "psutil",
        "requests",
        "daemonpy3"
    ],
    zip_safe=False,
    platforms=["Linux", "Unix"],
    classifiers = [
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        "console_scripts":[
            "start_worker = angel_worker.worker:serve_forever"
        ]
    }
)
