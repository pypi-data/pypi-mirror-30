#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-24
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_master.entity import *
from angel_master.entity.job import Job
from angel_master.entity.task import Task
from angel_master.entity.job_group import JobGroup
from angel_master.entity.job_depend import JobDepend
from angel_master.entity.task_group import TaskGroup
from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.exc import OperationalError
from traceback import format_exc

SessionBuilder = None


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
            raise
        except Exception as e:
            self.logger.warn(format_exc())
            raise
    return wrapper



class JobStore(object):
    """
    Implementation of Jobstore
    """

    def __init__(self, engine, logger):
        global SessionBuilder
        SessionBuilder = sessionmaker(bind=engine)
        self.engine = engine
        self.logger = logger
        m = MetaData(engine)
        self.j_t = Table("job", m,
                         Column('id', Integer, primary_key=True),
                         Column('group_id', Integer, ForeignKey('job_group.id')),
                         Column('name', String(64), nullable=False),
                         Column('desc', String(128)),
                         Column('worker_gid', Integer),
                         Column('trigger', String(32)),
                         Column('running_timeout', Integer, nullable=False))
        self.t_t = Table("task", m,
                         Column('id', Integer, primary_key=True),
                         Column('job_id', Integer, ForeignKey('job.id')),
                         Column('group_id', Integer, ForeignKey('job_group.id')),
                         Column('runtime', Integer, nullable=False),
                         Column('worker_id', Integer),
                         Column('done_time', Integer),
                         Column('state', Integer, default=Task.STATE_INIT))
        self.tg_t = Table("task_group", m,
                          Column('id', Integer, primary_key=True),
                          Column('group_id', Integer, ForeignKey('job_group.id')),
                          Column('runtime', Integer, nullable=False),
                          Column('done_time', Integer),
                          Column('state', Integer, nullable=False, default=Task.STATE_INIT))
        self.jg_t = Table("job_group", m,
                          Column('id', Integer, primary_key=True),
                          Column('name', String(64), nullable=False),
                          Column('desc', String(128)),
                          Column('first_job_id', Integer, ForeignKey('job.id')))
        self.jd_t = Table("job_depend", m,
                          Column('group_id', Integer, ForeignKey('job_group.id')),
                          Column('job1', Integer, ForeignKey('job.id'), primary_key=True),
                          Column('job2', Integer, ForeignKey('job.id'), primary_key=True))
        m.create_all()
        mapper(JobGroup, self.jg_t)
        mapper(Job, self.j_t)
        mapper(JobDepend, self.jd_t)
        mapper(TaskGroup, self.tg_t)
        mapper(Task, self.t_t)

    @except_logger
    def insert_task_group(self, group):
        session = SessionBuilder()
        session.add(group)
        session.commit()
        group.id = group.id
        session.close()

    @except_logger
    def insert_task(self, task):
        session = SessionBuilder()
        session.add(task)
        session.commit()
        task.id = task.id
        session.close()

    @except_logger
    def update_task(self, task_id, **kwargs):
        executable=self.t_t.update().where(self.t_t.c.id==task_id).values(**kwargs)
        self.engine.execute(executable)

    @except_logger
    def query_tasks(self, group_id):
        session = SessionBuilder()
        filter_ = Task.group_id==group_id
        tasks = session.query(Task).filter(filter_).all()
        session.close()
        return tasks

    @except_logger
    def update_task_group(self, group_id, **kwargs):
        executable=self.tg_t.update().where(self.tg_t.c.id==group_id).values(**kwargs)
        res = self.engine.execute(executable)

    @except_logger
    def query_task_group(self, group_id, runtime):
        session = SessionBuilder()
        filter_ = and_(TaskGroup.group_id==group_id, TaskGroup.runtime==runtime)
        groups = session.query(TaskGroup).filter(filter_).limit(1).all()
        session.close()
        if groups:
            return groups[0]

    @except_logger
    def query_all(self, group_id=None):
        session = SessionBuilder()
        if group_id:
            # query group
            groups = session.query(JobGroup).filter(JobGroup.id==group_id).one()
            if not groups:
                return (None, None, None)
            # query jobs
            jobs = session.query(Job).filter(Job.group_id==group_id).all()
            # query job_dependences
            job_depends = session.query(JobDepend).filter(JobDepend.group_id==group_id).all()
        else:
            # query group
            groups = session.query(JobGroup).all()
            if not groups:
                return (None, None, None)
            # query jobs
            jobs = session.query(Job).all()
            # query job_dependences
            job_depends = session.query(JobDepend).all()
        session.close()
        return (groups, jobs, job_depends)
