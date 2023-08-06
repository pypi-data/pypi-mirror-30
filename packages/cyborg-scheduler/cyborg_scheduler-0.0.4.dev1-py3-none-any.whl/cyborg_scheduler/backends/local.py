from .base import BaseBackend


class LocalBackend(BaseBackend):
    def __init__(self, cache_path=None):
        self._cache_path = cache_path

    def put_task(self, queue_id, task):
        pass

    def get_task(self, queue_id):
        pass

    def ack_task(self, queue_id, task_id):
        pass

    def nack_task(self, queue_id, task_id):
        pass

    def reject_task(self, queue_id, task_id):
        pass

    def info(self, queue_id):
        pass

    def queue_info(self, queue_id):
        pass

    def all_queue_info(self):
        pass
