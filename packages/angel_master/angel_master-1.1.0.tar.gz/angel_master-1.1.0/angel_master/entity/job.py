#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-07
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

class Job(object):
    """
    Contains the properties of Job, maps with the table 'job' in DB
    """
#    __slots__ = ("id", "group_id", "name", "desc", "worker_gid", "trigger", "expiry_time")
    def __init__(self, id=None, group_id=None, name=None, desc=None, worker_gid=None, trigger=None,
                 running_timeout=None):
        self.id = id
        self.group_id = group_id
        self.name = name
        self.desc = desc
        self.worker_gid = worker_gid
        self.trigger = trigger
        self.running_timeout = running_timeout

    def __str__(self):
        return "Job(id = %d, name = %s)" % (self.id, self.name)

    def __repr__(self):
        return "Job(id = %d, name = %s)" % (self.id, self.name)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, Job) and self.id == other.id


