
# @Time         2017-11-29
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93



class AbstractService(object):
    """
    Implementation of api service
    """

    def __init__(self, scheduler, resourcemanager, logger):
        self.scheduler = scheduler
        self.resourcemanager = resourcemanager
        self.logger = logger

    def login(self, name, password, worker_id):
        pass

    def register(self, name, password, params):
        pass

    def logout(self, worker_id):
        pass

    def all_alive_workers(self):
        pass

    def heartbeat(self, worker_id, params):
        pass

    def pull_tasks(self, worker_id):
        pass

    def pull(self, worker_id):
        pass

    def task_callback(self, task_id, done_time, worker_id, state):
        pass

    def add_log(self, task_id):
        pass

    def apply_job_group(self, group_id):
        pass

    def delete_job_group(self, group_id):
        pass

    def get_pending_tasks(self):
        pass

    def get_alive_tasks(self):
        pass

    def get_alive_job_groups(self):
        pass

    def get_alive_task_groups(self):
        pass

    def shutdown_workers(self, workers):
        pass
