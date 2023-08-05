#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-29
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


class AbstractServer(object):
    """
    Abstract RPCServer for remote procedure calls
    """

    def __init__(self, host, port, logger):
        self.host = host
        self.port = port
        self.logger = logger

    def start(self):
        """
        Startup the service
        """
        pass

    def stop(self):
        """
        Stop the service
        """
        pass

