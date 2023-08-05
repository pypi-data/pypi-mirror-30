#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2018-01-13
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


from setuptools import setup, find_packages
import sys
import os

ETC_PATH = "/etc/angel/master/"

setup(
    name="angel_master",
    version="1.1.0",
    author="Lafite93",
    author_email="2273337844@qq.com",
    description="The master of a distribute job scheduler named 'angel'",
    license="Apache",
    keywords="angel master",
    url="https://pypi.python.org/pypi/angel_master",
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        (ETC_PATH, ['etc/master.conf', 'etc/logger.conf'])
    ],
    scripts=["scripts/master_daemon"],
    install_requires=[
        "sqlalchemy",
        "configparser",
        "daemonpy3",
        "pymysql"
    ],
    zip_safe=False,
    platforms=["Linux", "Unix"],
    classifiers = [
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        "console_scripts":[
            "start_master = angel_master.master:serve_forever"
        ]
    }
)
