#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-07
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_master.entity.task import Task
from angel_master.core.dag import DAG
from angel_master.trigger.crontab import CrontabTrigger
from angel_master.entity.task_group import TaskGroup
from threading import Thread, Lock
import time


class DAGScheduler(object):
    def __init__(self, logger, jobstore):
        self.logger = logger
        self.jobstore = jobstore
        self.task_lock = Lock()
        self.job_lock = Lock()
        self.groups = {}
        self.job_dag = DAG()
        self.task_dag = DAG()
        self.job_groups = {}
        self.task_groups = {}
        self.jobs = {}
        self.tasks = {}

    def initialize(self, groups, jobs, job_dependences):
        if not groups:
            return
        # validate data
        _jobs = {}
        _job_groups = {}
        _job_depens = {}
        _illegal_groups = set()
        for group in groups:
            _job_groups[group.id] = []
            _job_depens[group.id] = []
        for job in jobs:
            _job_groups[job.group_id].append(job)
            _jobs[job.id] = job
            try:
                job.trigger = CrontabTrigger(job.trigger)
            except Exception as e:
                # TODO send a report
                self.logger.error("the trigger of  %s is illegal" % str(job))
                _illegal_groups.add(job.group_id)
        for group in groups:
            if not group.first_job_id or _jobs[group.first_job_id].group_id != group.id:
                # TODO send a report
                self.logger.error("the first job of the group %s is illegal" % str(group))
                _illegal_groups.add(group.id)
        for job_depend in job_dependences:
            job1 = _jobs[job_depend.job1]
            job2 = _jobs[job_depend.job2]
            if job_depend.group_id == job1.group_id == job2.group_id:
                _job_depens[job_depend.group_id].append((job1, job2))
            else:
                # TODO send a report
                self.logger.error("the job_depend %s is out of group" % str(job_depend))
                _illegal_groups.add(job_depend.group_id)
        # add job groups into jobs, job_groups, job_dag
        for group in groups:
            if group.id not in _illegal_groups:
                self._add_job_group(group, _job_groups[group.id], _job_depens[group.id])
        # release the memory
        del _jobs
        del _job_depens
        del _job_groups
        del _illegal_groups
        # remove cycles from job dag
        self._remove_job_cycles()
        # build task dag
        for group in groups:
            if group.id in self.job_groups:
                self._build_task_group(group.id)

    def _add_job_group(self, group, jobs, job_dependences):
        """
        Helper method for add a job group
        """
        with self.job_lock:
            if group.id in self.groups:
                # the group is already exist
                return
            self.groups[group.id] = group
            self.job_groups[group.id] = jobs
            for job in jobs:
                self.jobs[job.id] = job
                self.job_dag.add_node(job)
            for job_depend in job_dependences:
                self.job_dag.add_edge(job_depend[0], job_depend[1])

    def _remove_job_group(self, group_id):
        """
        Help method for remove a job group
        """
        with self.job_lock:
            if group_id not in self.groups:
                return
            del self.groups[group_id]
            jobs = self.job_groups.pop(group_id)
            for job in jobs:
                del self.jobs[job.id]
                self.job_dag.delete_node_if_exists(job)

    def _remove_job_cycles(self):
        """
        Helper method to remove cycle from job dag
        """
        with self.job_lock:
            # check if the job dag is acyclic
            if not self.job_dag.validate():
                topological_sort = self.job_dag.topological_sort()
                cycle_jobs = filter(lambda x: x not in topological_sort,
                                    self.jobs.values())
                group_ids = set(map(lambda x: x.group_id, cycle_jobs))
                for group_id in group_ids:
                    # TODO send a report
                    self.logger.error("jobs in the group(id=%d) is acyclic" % group_id)
                    sub_jobs = self.job_groups[group_id]
                    del self.job_groups[group_id]
                    del self.groups[group_id]
                    for job in sub_jobs:
                        del self.jobs[job.id]
                        self.job_dag.delete_node_if_exists(job)

    def _build_task_group(self, group_id):
        """
        Helper method to build new task by the given group_id
        """
        with self.job_lock:
            if group_id not in self.groups:
                return
            job_group = self.groups[group_id]
            now = int(time.time())
            jobs = self.job_groups[group_id]
            first_job = self.jobs[job_group.first_job_id]
            start_time = first_job.trigger.get_next_runtime(now, True)
            with self.task_lock:
                # check if the task group is already exist
                for item in self.task_groups.keys():
                    if item.runtime == start_time and item.group_id == group_id:
                        # TODO the task group is already exist
                        return
                # check if the task group is exist in database
                task_group = self.jobstore.query_task_group(group_id, start_time)
                if task_group is None:
                    flag = False
                    task_group = TaskGroup(group_id=group_id, runtime=start_time, state=Task.STATE_INIT)
                    self.jobstore.insert_task_group(task_group)
                else:
                    flag = True
                    tasks = self.jobstore.query_tasks(task_group.id)
                    tasks = {t.job_id: t for t in tasks}
                self.task_groups[task_group] = []
                job_task_map = {}
                # new task from job and set into tasks,task_groups,task_dag
                for job in jobs:
                    task = None
                    runtime = job.trigger.get_next_runtime(start_time, True)
                    if flag:
                        task = tasks.get(job.id)
                    if task is None:
                        task = Task(job_id=job.id, group_id=task_group.id, runtime=runtime)
                        # insert the task
                        self.jobstore.insert_task(task)
                    task.group = task_group
                    task.running_timeout = job.running_timeout
                    # add task node into task_dag, tasks, task_groups
                    self.tasks[task.id] = task
                    self.task_groups[task_group].append(task)
                    job_task_map[job] = task
                    self.task_dag.add_node(task)
                    # For dubug and testing
                    msg = str(task) + " will be executed at " + time.strftime("%m-%d %H:%M",
                                                                              time.localtime(task.runtime))
                    self.logger.debug(msg)
                # add task edge into task_dag
                for job in self.job_groups[group_id]:
                    task1 = job_task_map[job]
                    for job2 in self.job_dag.downstream(job):
                        task2 = job_task_map.get(job2)
                        if task2:
                            self.task_dag.add_edge(task1, task2)

    def _remove_task_group(self, job_group_id):
        """
        Helper method to remove task group by given job_group_id
        """
        with self.task_lock:
            groups = list(filter(lambda x: x.group_id == job_group_id,
                          self.task_groups.keys()))
            for group in groups:
                tasks = self.task_groups.pop(group)
                for task in tasks:
                    del self.tasks[task.id]
                    self.task_dag.delete_node_if_exists(task)

    def get_pending_tasks(self):
        """
        Return independent task, such as task in STATE_INIT, STATE_RUNNING
        """
        tasks = self.task_dag.ind_nodes()
        tmp = filter(lambda t: t.state == Task.STATE_INIT or t.state == Task.STATE_TIMING or
                     t.state == Task.STATE_RUNNING, tasks)
        return list(tmp)

    def is_task_group_finish(self, group):
        """
        Return if the tasks in the group are all success
        """
        tasks = self.task_groups.get(group)
        if tasks:
            for task in tasks:
                if task.state != Task.STATE_SUCCESS:
                    return False
            return True
        return False

    def on_task_success(self, task):
        """
        Remove the task after the task is success
        """
        del self.tasks[task.id]
        self.task_dag.delete_node_if_exists(task)
        if self.is_task_group_finish(task.group):
            # record the task group
            self.jobstore.update_task_group(task.group.id, state=Task.STATE_SUCCESS)
            # rebuild new task group
            self._build_task_group(task.group.group_id)
            del self.task_groups[task.group]

    def on_task_not_success(self, task):
        """
        Record the state of the task and alert
        """
        # revord the task group
        self.jobstore.update_task_group(task.group_id, state=Task.STATE_FAIL)
        # rebuild new task group
        self._build_task_group(task.group.group_id)

    def get_task(self, task_id):
        """
        Obtain task object by given task_id
        """
        return self.tasks.get(task_id)

    def add_job_group(self, group_id):
        """
        Force to add a job group by the given group id
        Besides, insert a new task dag
        """
        # encapsulate data and validate
        group, jobs, job_dependences = self.jobstore.query_all(group_id)
        _jobs = {}
        for job in jobs:
            try:
                job.trigger = CrontabTrigger(job.trigger)
            except Exception as e:
                # TODO the trigger of the job is illegal
                raise Exception("the trigger of  %s is illegal" % str(job))
            _jobs[job.id] = job
        if group.first_job_id not in _jobs:
            # TODO the first job id of the group is illegal
            raise Exception("the first job of the group %s is illegal" % str(group))
        _job_depends = []
        for job_depend in job_dependences:
            job1 = _jobs.get(job_depend.job1)
            job2 = _jobs.get(job_depend.job2)
            if job1 and job2 and job1.group_id == job2.group_id:
                _job_depends.append((job1, job2))
            else:
                # TODO the job dependence is illegal
                raise Exception('the job depend %s isillegal' % str(job_depend))
        # add into job dag
        self._add_job_group(group, jobs, _job_depends)
        # remove cycle from job dag if exist
        self._remove_job_cycles()
        # build a new task dag
        self._build_task_group(group.id)

    def delete_job_group(self, group_id):
        """
        Force to remove a job group by the given group id
        Besides, remove the tasks related
        """
        self._remove_job_group(group_id)
        self._remove_task_group(group_id)


class Scheduler(Thread):
    """
    A Scheduler that run in loops for time scheduler
    """

    def __init__(self, jobstore, resource_manager, scheduler_rule, logger,
                 scheduler_timeout, loop_time):
        super(Scheduler, self).__init__()
        self.jobstore = jobstore
        self.resource_manager = resource_manager
        self.scheduler_rule = scheduler_rule
        self.logger = logger
        self.scheduler_timeout = scheduler_timeout
        self.loop_time = loop_time
        self.started = False
        job_groups, jobs, job_dependences = self.jobstore.query_all()
        self.timing_tasks = []
        self.running_timeout_tasks = []
        self.dag_scheduler = DAGScheduler(logger, jobstore)
        self.dag_scheduler.initialize(job_groups, jobs, job_dependences)
        self.resource_manager.on_worker_remove = self.on_worker_remove

    def stop(self):
        self.started = False

    def run(self):
        """
        Main loop for time scheduler
        """
        self.started = True
        # check the status
        while self.started:
            pending_tasks = self.dag_scheduler.get_pending_tasks()
            # classify tasks according to their runtime
            running_timeout_tasks = []
            schedule_timeout_tasks = []
            timing_tasks = []
            now = int(time.time())
            schedule_timeout_time = now - self.scheduler_timeout
            for task in pending_tasks:
                if task.state == Task.STATE_INIT or task.state == Task.STATE_TIMING:
                    if task.runtime < schedule_timeout_time:
                        schedule_timeout_tasks.append(task)
                    elif task.runtime <= now:
                        timing_tasks.append(task)
                elif task.state == Task.STATE_RUNNING:
                    if task.runtime <= now - task.running_timeout:
                        running_timeout_tasks.append(task)
            # handle running timeout tasks
            self._handle_running_timeout(running_timeout_tasks)
            # handle schedule timeout tasks
            self._handle_schedule_timeout(schedule_timeout_tasks)
            # handle timing tasks
            self._handle_timing_tasks(timing_tasks)
            # sleep a moment
            time.sleep(self.loop_time)

    def _handle_running_timeout(self, tasks):
        """
        Handle running timeout tasks
        """
        now = int(time.time())
        for task in tasks:
            task.state = Task.STATE_RUNNING_TIMEOUT
            task.done_time = now
            # record the task state
            self.jobstore.update_task(task.id, state=Task.STATE_RUNNING_TIMEOUT, done_time=now)
            self.dag_scheduler.on_task_not_success(task)
            # info for debug
            self.logger.info("%s is running timeout" % str(task))
        self.running_timeout_tasks = tasks

    def _handle_schedule_timeout(self, tasks):
        """
        Handle schedule timeout tasks
        """
        now = int(time.time())
        for task in tasks:
            # reset its worker
            task.worker_id = None
            task.state = Task.STATE_SCHEDULE_TIMEOUT
            task.done_time = now
            # record the task state
            self.jobstore.update_task(task.id, state=Task.STATE_SCHEDULE_TIMEOUT, done_time=now)
            self.dag_scheduler.on_task_not_success(task)
            # TODO debug
            self.logger.debug("%s schedule timeout" % str(task))

    def _handle_timing_tasks(self, tasks):
        """
        Handle timing tasks
        """
        for task in tasks:
            # check if it has worker
            if task.worker_id:
                continue
            # get related worker list from resourceManager
            worker_gid = self.dag_scheduler.jobs[task.job_id].worker_gid
            worker_list = self.resource_manager.get_workers(worker_gid)
            # choose a worker according to scheduler rule
            worker = self.scheduler_rule.choose(worker_list)
            if worker:
                task.worker_id = worker.id
            # TODO debug
            self.logger.debug("%s is timming" % str(task))
        self.timing_tasks = tasks

    def get_task(self, task_id):
        """
        Return the task with the given task_id
        """
        return self.dag_scheduler.tasks.get(task_id)

    def pull_tasks(self, worker_id):
        """
        Return the tasks that should be executed and killed
        """
        # obtain the tasks that should be executed
        timing_tasks = list(filter(lambda task: task.worker_id == worker_id, self.timing_tasks))
        # obtain the tasks that should be terminated
        timeout_tasks = list(filter(lambda task: task.worker_id == worker_id, self.running_timeout_tasks))
        result = []
        for task in timing_tasks:
            # record the state STATE_RUNNING
            self.jobstore.update_task(task.id, state=Task.STATE_RUNNING, worker_id=worker_id)
            task.state = Task.STATE_RUNNING
            # serialize task in dict
            result.append({"id":task.id, "job_id":task.job_id, "state":Task.STATE_RUNNING})
        for task in timeout_tasks:
            # serialize task in dict
            result.append({"id":task.id, "job_id":task.job_id, "state":Task.STATE_RUNNING_TIMEOUT})
        return result

    def task_callback(self, task_id, done_time, worker_id, state):
        """
        Callback from worker when the task has been finish(success/fail)
        """
        # TODO for debug
        self.logger.debug("Task(id=%s,wid=%s,state=%s) callback" % (task_id, worker_id, state))
        # record the task state
        self.jobstore.update_task(task_id, state=state, done_time=done_time)
        task = self.dag_scheduler.get_task(task_id)
        if task:
            task.state = state
            # dag schedule
            if state == Task.STATE_SUCCESS:
                self.dag_scheduler.on_task_success(task)
            else:
                self.dag_scheduler.on_task_not_success(task)

    def add_job_group(self, group_id):
        """
        Add a job group from DB by the given group_id
        """
        self.dag_scheduler.add_job_group(group_id)

    def delete_job_group(self, group_id):
        """
        Delete a job group by the given group_id
        """
        self.dag_scheduler.delete_job_group(group_id)

    def pending_tasks(self):
        tasks = self.dag_scheduler.get_pending_tasks()
        result = []
        for task in tasks:
            result.append(task.to_dict())
        return result

    def alive_tasks(self):
        tasks = self.dag_scheduler.tasks.values()
        result = []
        for task in tasks:
            result.append(task.to_dict())
        return result

    def alive_job_groups(self):
        groups = self.dag_scheduler.groups.values()
        result = []
        for group in groups:
            result.append(group.to_dict())
        return result

    def alive_task_groups(self):
        groups = self.dag_scheduler.task_groups.keys()
        result = []
        for group in groups:
            result.append(group.to_dict())
        return result

    def on_worker_remove(self, worker):
        """
        Callback from resourceManager when the worker is timeout
        """
        tasks = filter(lambda task: task.worker_id == worker.id,
                       self.timing_tasks)
        for task in tasks:
            task.worker_id = None
