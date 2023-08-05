#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-27
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


class AbstractRule(object):
    """
    Interface of Scheduler rule
    """

    def choose(self, workers):
        """
        Choose one of the given workers, to execute task
        """
        pass
