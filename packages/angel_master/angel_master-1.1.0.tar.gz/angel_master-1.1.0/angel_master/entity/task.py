#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-07
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


class Task(object):
    """
    Contains the properties of task, which is the instance of Job
    """

    #__slots__ = ("id", "job_id", "group", "group_id", "runtime", "worker_id", "running_timeout", "done_time", "state")

    STATE_INIT = 100
    STATE_TIMING = 101
    STATE_RUNNING = 102
    STATE_SCHEDULE_TIMEOUT = 103
    STATE_RUNNING_TIMEOUT = 104
    STATE_DOWNLOAD_FAIL = 105
    STATE_SUCCESS = 0
    STATE_FAIL = 1

    #INIT_STATE = 0
    #TIMING_STATE = 1
    #SUCCESS_STATE = 2
    #RUNNING_STATE = 3
    #SCHEDULE_TIMEOUT_STATE = 4
    #RUNNING_TIMEOUT_STATE = 5
    #FAIL = 6

    def __init__(self, id=None, job_id=None, group_id=None, runtime=None, running_timeout=None,
                 worker_id=None, done_time=None, state=STATE_INIT):
        self.id = id
        self.job_id = job_id
        self.group_id = group_id
        self.runtime = runtime
        self.running_timeout = running_timeout
        self.worker_id = worker_id
        self.done_time = done_time
        self.state = state

    def __str__(self):
        return "Task(id=%d, job_id=%d, runtime=%d)" % (self.id, self.job_id, self.runtime)

    def __repr__(self):
        return "Task(id=%d, job_id=%d, runtime=%d)" % (self.id, self.job_id, self.runtime)

    def __hash__(self):
        return (self.runtime & 65535) * self.job_id

    def __eq__(self, other):
        return isinstance(other, Task) and self.runtime == other.runtime and \
                self.job_id == other.job_id

    def to_dict(self):
        return {"id":self.id, "job_id":self.job_id, "group_id":self.group_id,
                "runtime":self.runtime, "worker_id":self.worker_id, "done_time":self.done_time,
                "state":self.state}

