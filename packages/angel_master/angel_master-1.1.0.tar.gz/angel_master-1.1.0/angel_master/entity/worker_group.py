#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-07
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

class WorkerGroup(object):
    __slots__ = ("id", "name", "desc")

    def __str__(self):
        return "WorkerGroup(id = %d, name = %s)" % (self.id, self.name)

    def __repr__(self):
        return "WorkerGroup(id = %d, name = %s)" % (self.id, self.name)

    def __eq__(self, other):
        return isinstance(other, WorkerGroup) and self.id == other.id

