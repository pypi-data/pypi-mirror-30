#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-29
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_master.api.base_service import AbstractService
from traceback import format_exc

CODE_SUCCESS = 0
CODE_FAIL = 1
on_logs = dict()
off_workers = set()


def exception_handler(func):
    """
    Decorator for obtaining the response after calling service
    When a exception raised, the response returns CODE_ERROR
    """
    def wrapper(self, *args, **kwargs):
        resp = {}
        try:
            result = func(self, *args, **kwargs)
            resp["code"] = CODE_SUCCESS
            if result is not None:
                resp["content"] = result
        except Exception as e:
            resp["code"] = CODE_FAIL
            resp["content"] = str(e)
            self.logger.warn(format_exc())
        return resp
    return wrapper


class RPCService(AbstractService):
    """
    Implementation of api service
    """

    def __init__(self, scheduler, resourcemanager, logger):
        self.scheduler = scheduler
        self.resourcemanager = resourcemanager
        self.logger = logger

    @exception_handler
    def login(self, name, password, worker_id):
        return self.resourcemanager.login(name, password, worker_id)

    @exception_handler
    def register(self, name, password, params):
        return self.resourcemanager.register(name, password, params)

    @exception_handler
    def logout(self, worker_id):
        return self.resourcemanager.logout(worker_id)

    @exception_handler
    def all_alive_workers(self):
        workers = self.resourcemanager.get_workers()
        result = []
        for worker in workers:
            result.append({"id":worker.id, "cpu_free":worker.cpu_free,
                           "memory_free":worker.memory_free, "disk_write":worker.disk_write,
                           "disk_read":worker.disk_read, "net_send":worker.net_send,
                           "net_rev":worker.net_rev, "running_tasks":worker.running_tasks,
                           "refresh_time":worker.refresh_time})
        return result

    @exception_handler
    def heartbeat(self, worker_id, params):
        return self.resourcemanager.heartbeat(worker_id, params)

    @exception_handler
    def pull_tasks(self, worker_id):
        return self.scheduler.pull_tasks(worker_id)

    @exception_handler
    def pull(self, worker_id):
        if worker_id in off_workers:
            off_workers.remove(worker_id)
            return {"cmd":"shutdown"}
        result = {}
        tasks = self.scheduler.pull_tasks(worker_id)
        if tasks:
            result["tasks"] = tasks
        if worker_id in on_logs:
            result["logs"] = list(on_logs.pop(worker_id))
        return result

    @exception_handler
    def task_callback(self, tasks):
        for task in tasks:
            self.scheduler.task_callback(*task)

    @exception_handler
    def add_log(self, task_id):
        task_id = int(task_id)
        task = self.scheduler.get_task(task_id)
        if task is None or task.worker_id is None:
            raise Exception("the task(id=%d) is not running" % task_id)
        worker_id = task.worker_id
        if self.resourcemanager.get_worker(worker_id) is None:
            raise Exception("The worker running the task is death")
        if worker_id in on_logs:
            on_logs[worker_id].add(task_id)
        else:
            on_logs[worker_id] = set([task_id])

    @exception_handler
    def apply_job_group(self, group_id):
        self.scheduler.delete_job_group(group_id)
        self.scheduler.add_job_group(group_id)

    @exception_handler
    def delete_job_group(self, group_id):
        self.scheduler.delete_job_group(group_id)

    @exception_handler
    def get_pending_tasks(self):
        return self.scheduler.pending_tasks()

    @exception_handler
    def get_alive_tasks(self):
        return self.scheduler.alive_tasks()

    @exception_handler
    def get_alive_job_groups(self):
        return self.scheduler.alive_job_groups()

    @exception_handler
    def get_alive_task_groups(self):
        return self.scheduler.alive_task_groups()

    @exception_handler
    def shutdown_workers(self, workers):
        off_workers = off_workers.union(set(workers))
