#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-24
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

class JobDepend(object):
    """
    Job Dependence
    (job1, job2) means that the job2 has to run after job1
    """
#    __slots__ = ('job1', 'job2')

    def __init__(self, group_id=None, job1=None, job2=None):
        self.group_id = group_id
        self.job1 = job1
        self.job2 = job2

    def __str__(self):
        return "JobDepend(group_id=%d, job1=%d, job2=%d)" % (self.group_id, self.job1, self.job2)
