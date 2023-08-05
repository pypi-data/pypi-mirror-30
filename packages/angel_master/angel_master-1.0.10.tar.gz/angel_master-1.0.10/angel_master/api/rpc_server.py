#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-29
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_master.api.base_server import AbstractServer
from angel_master.api.rpc_service import RPCService
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn


class ThreadingXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class XMLRPCServer(AbstractServer):
    """
    RPCServer implemented with xmlrpc.server
    """

    def __init__(self, host, port, logger, scheduler, resourcemanager):
        super(XMLRPCServer, self).__init__(host, port, logger)
        rpc_service = RPCService(scheduler, resourcemanager, logger)
        #self.server = SimpleXMLRPCServer((host, int(port)), logRequests=False)
        self.server = ThreadingXMLRPCServer((host, port), logRequests=False, allow_none=True)
        self.server.register_instance(rpc_service)

    def start(self):
        """
        Startup the service
        """
        try:
            self.server.serve_forever()
        except Exception as e:
            self.logger.warn("rpc server start fail caused by %s" % str(e))
            raise

    def stop(self):
        """
        Stop the service
        """
        try:
            self.server.server_close()
        except Exception as e:
            self.logger.warn("rpc server stop fail caused by %s" % str(e))
            raise
