from sortedcontainers import SortedListWithKey
from pyee import EventEmitter

from .token_bucket import Bucket

# task = {
#     'id': str, //backend生成
#     'meta': {
#         'max_retry': int
#     },
#     'body': str
# }


class TaskQueue(EventEmitter):
    def __init__(self, scheduler, queue_id, priority=0, max_retry=5,
                 rate=1, burst=None):
        super().__init__()
        self.scheduler = scheduler
        self.backend = self.scheduler.backend
        self.id = queue_id
        self.priority = priority
        self.max_retry = max_retry
        burst = burst or (rate if rate > 1 else 1)
        self.bucket = Bucket(rate=rate, burst=burst)

    def _new_task(self, task_body):
        return dict(
            meta=dict(
                max_retry=self.max_retry
            ),
            body=task_body
        )

    def config(self):
        return dict(
            priority=self.priority,
            max_retry=self.max_retry,
            rate=self.bucket.rate,
            burst=self.bucket.burst
        )

    @property
    def is_ready(self):
        return self.bucket.get() >= 1

    def ready(self):
        self.emit('ready', self.id)

    def check_ready(self):
        if self.is_ready:
            self.ready()

    def ack(self, task_id):
        r = self.backend.ack_task(self.id, task_id)
        if r:
            self.emit('ack_task', self.id)
        return r

    def nack(self, task_id):
        r = self.backend.nack_task(self.id, task_id)
        if r:
            self.emit('nack_task', self.id)
        return r

    def get(self):
        if not self.is_ready:
            return None

        task = self.backend.get_task(self.id)

        if task is None:
            return task

        self.emit('get_task', self.id)
        self.bucket.desc()
        self.check_ready()
        return task

    def put(self, task_body):
        task = self._new_task(task_body)
        task_id = self.backend.put_task(self.id, task)
        if task_id:
            self.emit('put_task', self.id)
        return task_id

    def reject(self, task_id):
        r = self.self.backend.reject_task(self.id, task_id)
        if r:
            self.emit('reject_task', self.id)
        return r

class TQPEventCallback(object):
    def __init__(self, pool):
        self.pool = pool

    def on_ready(self, queue_id):
        task_queue = self.pool.get(queue_id)
        if task_queue and task_queue not in self.pool._ready_queues:
            self.pool._ready_queues.add(task_queue)


class TaskQueuePool(object):
    def __init__(self, scheduler):
        self.scheduler = scheduler

        self._event_callback = TQPEventCallback(self)
        self._queues = dict()
        self._ready_queues = SortedListWithKey(key=lambda q: q.priority)

    def check_queues(self):
        for task_queue in self._queues.values():
            task_queue.check_ready()

    def register(self, queue_id, **kwargs):
        task_queue = TaskQueue(self.scheduler, queue_id, **kwargs)
        self.add(task_queue)
        return task_queue

    def add(self, task_queue):
        self._queues[task_queue.id] = task_queue
        task_queue.on('ready', self._event_callback.on_ready)

    def get(self, queue_id):
        return self._queues.get(queue_id, None)

    def select(self):
        if len(self._ready_queues) > 0:
            return self._ready_queues.pop()

    def unregister(self, queue_id):
        task_queue = self.get(queue_id)
        if task_queue:
            task_queue.remove_listener('ready', self._event_callback.on_ready)
            del self._queues[task_queue.id]
            if task_queue in self._ready_queues:
                self._ready_queues.remove(task_queue)
