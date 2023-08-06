import importlib
import copy

from cyborg_scheduler.task_queue import TaskQueuePool
from cyborg_scheduler.monitor import MonitorMock, Monitor
from cyborg_scheduler.backends.local import LocalBackend


class Scheduler(object):
    def __init__(self, backend_class=LocalBackend, backend_kwargs={},
                 daemon=False, monitor=False):
        self.backend_class = backend_class
        self.backend_kwargs = backend_kwargs

        if monitor:
            self._monitor = Monitor(self)
        else:
            self._monitor = MonitorMock(self)

        self._daemon = daemon
        self._running = False
        self._task_queue_pool = TaskQueuePool(self)
        self._dispatch_callback = lambda *args, **kwargs: None

        self._init_periods()

        self.start()

    def _init_periods(self):
        if not self.is_daemon:
            return
        self._check_period = self.tornado_ioloop.\
            PeriodicCallback(self.check, 100)
        self._check_period.start()

    @property
    def monitor(self):
        return self._monitor

    @property
    def io_loop(self):
        if self._daemon:
            return self.tornado_ioloop.IOLoop.current()
        else:
            None

    @property
    def tornado_ioloop(self):
        if self.is_daemon:
            return importlib.import_module('tornado.ioloop')

    @property
    def is_daemon(self):
        return self._daemon

    def check(self):
        if self._running:
            self._task_queue_pool.check_queues()
            self.backend.check()

    def start(self):
        if (self._running):
            return
        self.backend = self.backend_class(**self.backend_kwargs)
        self._running = True

    def start_dispatch(self):
        if not self.is_daemon:
            raise Exception('"start_dispatch" only called in daemon mode')

        self.start()
        self.__poll()

    def get_queue_config(self, queue_id):
        return self._task_queue_pool.get(queue_id).config()

    def get_task(self, queue_id=None):
        queue_id, task = self._get_task(queue_id)
        if task:
            meta = copy.copy(task['meta'])
            meta['queue_id'] = queue_id
            meta['task_id'] = task['id']
            return [meta, task['body']]
        else:
            return [None, None]

    def _get_task(self, queue_id=None):
        if not self.is_daemon:
            self.check()
        if queue_id is None:
            task_queue = self._task_queue_pool.select()
        else:
            task_queue = self._task_queue_pool.get(queue_id)
        task = task_queue and task_queue.get()
        return [task_queue.id, task] if task else [None, None]

    def __poll(self):
        queue_id, task = self._get_task()
        if task:
            self._dispatch_callback(queue_id, task)
            self.io_loop.call_later(0, self.__poll)
        else:
            self.io_loop.call_later(0.1, self.__poll)

    def on_dispatch(self, callback):
        self._dispatch_callback = callback

    def register(self, queue_id, **kwargs):
        task_queue = self._task_queue_pool.register(queue_id, **kwargs)
        self.monitor.register(task_queue)

    def publish(self, queue_id, task_body):
        task_queue = self._task_queue_pool.get(queue_id)
        if task_queue:
            return task_queue.put(task_body)

    def ack(self, queue_id, task_id):
        task_queue = self._task_queue_pool.get(queue_id)
        if task_queue:
            return task_queue.ack(task_id)

    def nack(self, queue_id, task_id):
        task_queue = self._task_queue_pool.get(queue_id)
        if task_queue:
            return task_queue.nack(task_id)

    def reject(self, queue_id, task_id):
        task_queue = self._task_queue_pool.get(queue_id)
        if task_queue:
            return task_queue.reject(task_id)
