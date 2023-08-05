#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-27
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_master.scheduler_rule.base import AbstractRule
import random


class RandomRule(AbstractRule):
    """
    Random rule of choosing worker
    """

    def choose(self, workers):
        if workers:
            return random.choice(workers)
