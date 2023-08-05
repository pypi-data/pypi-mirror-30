#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-07
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

class JobGroup(object):
    """
    Contains the properties of JobGroup, maps with the table 'job_group' in DB
    """
#    __slots__ = ("id", "name", "desc", "first_job_id")

    def __init__(self, id=None, name=None, desc=None, first_job_id=None):
        self.id = id
        self.name = name
        self.desc = desc
        self.first_job_id = first_job_id

    def __str__(self):
        return "JobGroup(id = %d, name = %s)" % (self.id, self.name)

    def __repr__(self):
        return "JobGroup(id = %d, name = %s)" % (self.id, self.name)

    def __eq__(self, other):
        return isinstance(other, JobGroup) and self.id == other.id

    def to_dict(self):
        return {"id":self.id, "name":self.name, "desc":self.desc, "first_job_id":self.first_job_id}

