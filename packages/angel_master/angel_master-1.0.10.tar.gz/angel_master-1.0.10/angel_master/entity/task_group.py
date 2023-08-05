#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-07
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


class TaskGroup(object):
    """
    Contains the properties of task, which is the instance of Job
    """

    #__slots__ = ("id", "group_id", "runtime", "done_time", "state")

    def __init__(self, id=None, group_id=None, runtime=None, state=None):
        self.id = id
        self.group_id = group_id
        self.runtime = runtime
        self.state = state

    def __str__(self):
        return "TaskGroup(id = %d, group_id = %d, runtime = %d)" % (self.id, self.group_id,
                                                                    self.runtime)

    def __repr__(self):
        return "TaskGroup(id = %d, group_id = %d, runtime = %d)" % (self.id, self.group_id,
                                                                    self.runtime)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, TaskGroup) and self.id == other.id

    def to_dict(self):
        return {"id":self.id, "group_id":self.group_id, "runtime":self.runtime,
                "done_time":self.done_time, "state":self.state}

