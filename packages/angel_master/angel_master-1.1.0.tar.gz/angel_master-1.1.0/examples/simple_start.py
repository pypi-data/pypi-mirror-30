#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-27
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from angel_master import master
#from sqlalchemy import *
#from sqlalchemy.orm import sessionmaker, mapper
#from master.entity.job import Job
#from master.entity.task import Task
#from master.entity.task_group import TaskGroup
#from master.entity.job_group import JobGroup
#from master.entity.job_depend import JobDepend
#from master.jobstore.jobstore import JobStore

if __name__ !=  '__main__':
    exit()

#engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/angel')
#m = MetaData(engine)
## mapper
#m = MetaData(engine)
#j_t = Table("job", m, Column('id', Integer, primary_key=True),
#            Column('group_id', Integer, ForeignKey('job_group.id')),
#            Column('name', String(64), nullable=False),
#            Column('desc', String(128)),
#            Column('worker_gid', Integer),
#            Column('trigger', String(32)),
#            Column('running_timeout', Integer, nullable=False))
#t_t = Table("task", m, Column('id', Integer, primary_key=True),
#            Column('job_id', Integer, ForeignKey('job.id')),
#            Column('group_id', Integer, ForeignKey('task_group.id')),
#            Column('runtime', Integer, nullable=False),
#            Column('worker_id', Integer),
#            Column('done_time', Integer),
#            Column('state', Integer, default=Task.INIT_STATE))
#tg_t = Table("task_group", m, Column('id', Integer, primary_key=True),
#             Column('group_id', Integer, ForeignKey('job_group.id')),
#             Column('runtime', Integer, nullable=False),
#             Column('done_time', Integer),
#             Column('state', Integer, nullable=False, default=Task.INIT_STATE))
#jg_t = Table("job_group", m, Column('id', Integer, primary_key=True),
#             Column('name', String(64), nullable=False),
#             Column('desc', String(128)),
#             Column('first_job_id', Integer))
#jd_t = Table("job_depend", m, Column('group_id', Integer, ForeignKey('job_group.id')),
#             Column('job1', Integer, ForeignKey('job.id'), primary_key=True),
#             Column('job2', Integer, ForeignKey('job.id'), primary_key=True))
#m.create_all()
#mapper(JobGroup, jg_t)
#mapper(Job, j_t)
#mapper(JobDepend, jd_t)
#mapper(TaskGroup, tg_t)
#mapper(Task, t_t)
#
#SessionBuilder = sessionmaker(engine)
#session = SessionBuilder()
## clean data
#session.query(Job).delete()
#session.query(JobGroup).delete()
#session.query(JobDepend).delete()
#session.commit()
#
## insert data
#jg1 = JobGroup(id=1, name='group1', first_job_id=1, desc='It is group1')
#jg2 = JobGroup(id=2, name='group2', first_job_id=5, desc='It is group2')
#job1 = Job(id=1, group_id=1, name='A', desc='jobA', running_timeout=60, trigger='0 * * * *')
#job2 = Job(id=2, group_id=1, name='B', desc='jobB', running_timeout=60, trigger='1 * * * *')
#job3 = Job(id=3, group_id=1, name='C', desc='jobC', running_timeout=60, trigger='2 * * * *')
#job4 = Job(id=4, group_id=1, name='D', desc='JobE', running_timeout=60, trigger='3 * * * *')
#job5 = Job(id=5, group_id=2, name='E', desc='jobF', running_timeout=60, trigger='4 * * * *')
#job6 = Job(id=6, group_id=2, name='F', desc='JobD', running_timeout=60, trigger='5 * * * *')
#job7 = Job(id=7, group_id=2, name='G', desc='jobG', running_timeout=60, trigger='6 * * * *')
#session.add(jg1)
#session.add(jg2)
#session.commit()
#session.add(job1)
#session.add(job2)
#session.add(job3)
#session.add(job4)
#session.add(job5)
#session.add(job6)
#session.add(job7)
#session.commit()
#session.close()

master.serve_ha(debug=True)
