#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-27
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_master.resource_manager import ResourceManager
from angel_master.scheduler import Scheduler
from angel_master.jobstore import JobStore
from angel_master.scheduler_rule.rand import RandomRule
from angel_master.core import config_util
from angel_master.api.rpc_server import XMLRPCServer
from sqlalchemy import create_engine
from traceback import format_exc
import logging
import logging.config
import os

ETC_PATH = "/etc/angel/master/"

client = None
service_url = None
debug_ = False
config = None
logger = None

def serve_ha(debug=False):
    global client
    global debug_
    global logger
    global config
    global service_url
    debug_ = debug
    # setup logger
    logger_config_path = os.path.join(ETC_PATH, "logger.conf")
    logging.config.fileConfig(logger_config_path)
    if debug:
        logger = logging.getLogger("debug")
    else:
        logger = logging.getLogger("release")
    # load setting
    config_path = os.path.join(ETC_PATH, "master.conf")
    if not os.path.isfile(config_path):
        logger.error("configuration file %s not exist" % config_path)
    try:
        # import settings
        config = config_util.parse(config_path, 'master')
        ha_flag = config["ha"].lower() == "true"
        host = config["host"]
        port = int(config["port"])
        service_url = "http://{0}:{1}".format(host, port)
        if ha_flag:
            # start the service in ha mode
            etcd_urls = config["etcd_urls"].split(",")
            namespace = config["namespace"]
    except Exception as e:
        logger.error("config file '%s' error: %s" %(config_path, format_exc()))
        raise
    if ha_flag:
        import etcd3ctl
        client = etcd3ctl.Client(namespace, _on_resume, _on_pause, urls=etcd_urls)
        client.setup_etcd_server()
        success = client.register_service(service_url)
        if success:
            logger.info("the master service start as active mode")
            serve_forever(debug=True, config=config, logger=logger)
        else:
            logger.info("the master service start as standby mode")
            client.watch_callback()
    else:
        # start the service in single mode
        serve_forever(debug=True, config=config, logger=logger)

def serve_forever(debug, config, logger):
    try:
        # import settings
        name = config['name']
        pwd = config['password']
        host = config["host"]
        port = int(config["port"])
        db_url = config["db_url"]
        max_overflow = int(config["max_overflow"])
        heartbeat_loop_time = int(config["heartbeat_loop_time"])
        worker_timeout = int(config["worker_timeout"])
        schedule_timeout = int(config["schedule_timeout"])
        schedule_loop_time = int(config["schedule_loop_time"])
    except Exception as e:
        logger.error("config file '%s' error: %s" %(config_path, format_exc()))
        raise
    logger.info("Master service is starting")
    # init db engine
    engine = create_engine(db_url, max_overflow=max_overflow)
    # init resource manager
    resource_manager = ResourceManager(logger, heartbeat_loop_time, worker_timeout, engine, name, pwd)
    # init jobstore
    jobstore = JobStore(engine, logger)
    # init scheduler
    rule = RandomRule()
    scheduler = Scheduler(jobstore, resource_manager, rule, logger, schedule_timeout, schedule_loop_time)
    # init rpc service
    rpc_server = XMLRPCServer(host, port, logger, scheduler, resource_manager)
    # startup resource manager
    resource_manager.start()
    # start up scheduler
    scheduler.start()
    # start up rpc service
    rpc_server.start()

def _on_pause():
    logger.info("master service is stopped")
    success = client.register_service(service_url)
    if success:
        serve_forever(debug_, config, logger)

def _on_resume():
    logger.info("the master service started: " + client.get_current_service_url())
