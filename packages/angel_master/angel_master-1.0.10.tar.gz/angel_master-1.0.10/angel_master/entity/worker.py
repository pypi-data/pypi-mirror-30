#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-07
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

import time


class Worker(object):
    """
    Contains the properties of Worker
    """
    __slots__ = ("id", "group_id", "cpu_free", "memory_free", "disk_write", "disk_read",
                 "net_send", "net_rev",  "running_tasks", "refresh_time", "desc")

    def __init__(self, worker_id=0, group_id=None, desc=None, refresh_time=int(time.time())):
        self.id = worker_id
        self.group_id = group_id
        self.desc = desc
        self.refresh_time = refresh_time
        self.cpu_free = 0
        self.memory_free = 0
        self.disk_write = 0
        self.disk_read= 0
        self.net_send = 0
        self.net_rev = 0
        self.running_tasks = 0

    def __str__(self):
        return "Worker(id = %s)" % self.id

    def __repr__(self):
        return "Worker(id = %s)" % self.id

    def __eq__(self, other):
        return isinstance(other, Worker) and self.id == other.id

