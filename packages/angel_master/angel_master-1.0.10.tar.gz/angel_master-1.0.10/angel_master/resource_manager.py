#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-22
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from sqlalchemy import *
from sqlalchemy.exc import OperationalError
from angel_master.entity.worker import Worker
from traceback import format_exc
from threading import Thread
import time
import hashlib


def except_logger(func):
    """
    Decorator for logging when raising exception
    when a exception raised, the decorator will log it and raise again
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except OperationalError as e:
            self.logger.error("couldn't execute db engine, %s" % str(e))
            # TODO report an incident to the admin
            raise
        except Exception as e:
            self.logger.warn(format_exc())
            raise
    return wrapper

worker_t = None
wg_t = None


class ResourceManager(Thread):
    """
    Implementation of resource manager
    """

    def __init__(self, logger, loop_time, timeout, engine, name, pwd):
        super(ResourceManager, self).__init__()
        global worker_t
        global wg_t
        self.started = False
        self.logger = logger
        self.loop_time = loop_time
        self.on_worker_remove = None
        self.timeout = timeout
        # obtain the hash of name
        self.name = hashlib.sha1(name.encode("utf8")).hexdigest()
        # obtain the hash of password
        self.pwd = hashlib.sha1(pwd.encode("utf8")).hexdigest()
        self.engine = engine
        metadata = MetaData(engine)
        wg_t = Table("worker_group", metadata,
                     Column("id", Integer, primary_key=True),
                     Column("name", String(64), nullable=False),
                     Column("desc", String(128)))
        worker_t = Table("worker", metadata,
                        Column('id', Integer, primary_key = True),
                        Column('group_id', Integer, ForeignKey('worker_group.id')),
                        Column('login_time', Integer),
                        Column('desc', String(128)))
        metadata.create_all()
        # key is group id and value is list of the worker
        self.worker_groups = {}
        # key is worker_id and value is worker
        self.workers = {}

    def stop(self):
        self.started = False

    def run(self):
        """
        Main loop for scheculer
        """
        self.started = True
        while self.started:
            # sleep for a while
            time.sleep(self.loop_time)
            # calculate the timeout thredshold time
            thredshold = int(time.time()) - self.timeout
            # filter all workers using the thredshold time
            workers = list(filter(lambda x:x.refresh_time < thredshold, self.workers.values()))
            for worker in workers:
                self.logger.debug("%s timeout" % worker)
                # remove the worker
                del self.workers[worker.id]
                if worker.group_id in self.worker_groups:
                    ll = self.worker_groups[worker.group_id]
                    if worker in ll:
                        ll.remove(worker)
                # send message to listener
                if self.on_worker_remove:
                    self.on_worker_remove(worker)

    def heartbeat(self, worker_id, params):
        # find the worker
        worker = self.workers.get(worker_id)
        if not worker:
            self.login(self.name, self.pwd, worker_id)
        # update the parameters
        worker = self.workers.get(worker_id)
        worker.refresh_time = int(time.time())
        for k,v in params.items():
            if k in worker.__slots__:
                setattr(worker, k, v)

    @except_logger
    def register(self, name, pwd, params):
        # check if the name and pwd is legal
        if self.name == name and self.pwd == pwd:
            # insert into database
            now = int(time.time())
            params["login_time"] = now
            res = worker_t.insert().execute(params)
            ids = res.inserted_primary_key
            if len(ids) == 1:
                return ids[0]
            raise Exception("register fail caused by %d records were insert" % len(ids))
        raise Exception("register fail caused by password or name is wrong")

    @except_logger
    def login(self, name, pwd, worker_id):
        if self.name == name and self.pwd == pwd:
            # check if the worker is register
            executable = select([worker_t.c.group_id]).where(worker_t.c.id == worker_id)
            res = self.engine.execute(executable)
            result = res.fetchall()
            if result and result[0]:
                # set the worker into data structure
                gid = result[0][0]
                now = int(time.time())
                worker = Worker(worker_id=worker_id, group_id=gid, refresh_time=now)
                self.workers[worker_id] = worker
                if gid not in self.worker_groups:
                    self.worker_groups[gid] = []
                ll = self.worker_groups[gid]
                if worker not in ll:
                    ll.append(worker)
                # update the worker's last login time
                worker_t.update().where(worker_t.c.id==worker_id).values(login_time=now)
                # info for debug
                self.logger.info("worker(wid=%d) login successfully" % worker_id)
            else:
                raise Exception("login fail caused by not register before")
        else:
            raise Exception("login fail caused by password or name is wrong")

    def logout(self, worker_id):
        # remove the worker out of data structure
        if worker_id in self.workers:
            worker = self.workers[worker_id]
            del self.workers[worker_id]
            if worker.group_id in self.worker_groups:
                ll = self.worker_groups[worker.group_id]
                if worker in ll:
                    ll.remove(worker)
                    if not ll:
                        del self.worker_groups[worker.group_id]
        # send a message to the listener
        if self.worker_listener:
            self.worker_listener.on_worker_remove(worker)

    def get_workers(self, group_id=None):
        """
        Obtain alive workers with the given group_id
        Return all alive workers when group_id is None
        """
        if group_id:
            return self.worker_groups.get(group_id)
        else:
            return list(self.workers.values())

    def get_worker(self, worker_id):
        """
        Return the alive worker with the given worker_id
        """
        return self.workers.get(worker_id)
