import time
import copy


class MonitorMock(object):
    def __init__(self, scheduler):
        self.scheduler = scheduler

    def register(self, task_queue):
        pass

    def unregister(self, task_queue):
        pass

    def snapshot(self):
        pass


class MonitorEventCallback(object):
    event_names = ('get_task', 'put_task', 'ack_task', 'nack_task')

    def __init__(self, monitor):
        self.monitor = monitor

    def incr(self, queue_id, name):
        stats = self.monitor._stats[queue_id]
        if stats:
            stats[name] += 1

    def get_task(self, queue_id, *args):
        self.incr(queue_id, 'get_task')

    def put_task(self, queue_id, *args):
        self.incr(queue_id, 'put_task')

    def ack_task(self, queue_id, *args):
        self.incr(queue_id, 'ack_task')

    def nack_task(self, queue_id, *args):
        self.incr(queue_id, 'nack_task')


class Monitor(MonitorMock):
    def __init__(self, scheduler):
        super().__init__(scheduler)

        self._stats = {}
        self._event_callback = MonitorEventCallback(self)

    def _reset_stats(self, queue_id=None):
        monitor = self

        def reset_stats(queue_id):
            monitor._stats[queue_id] = dict(
                get_task=0,
                put_task=0,
                ack_task=0,
                nack_task=0,
                timestamp=time.time()
            )
        if queue_id is None:
            for _queue_id in self._stats:
                reset_stats(_queue_id)
        else:
            reset_stats(queue_id)

    def register(self, task_queue):
        self._reset_stats(task_queue.id)
        for event_name in self._event_callback.event_names:
            callback = getattr(self._event_callback, event_name)
            task_queue.on(event_name, callback)

    def unregister(self, task_queue):
        self._stats.pop(task_queue.id)
        for event_name in self._event_callback.event_names:
            callback = getattr(self._event_callback, event_name)
            task_queue.remove_listener(event_name, callback)

    def snapshot(self, name):
        if name == 'backend_info':
            return self.snapshot_backend_info()
        elif name == 'queues_info':
            return self.snapshot_queues_info()
        elif name == 'queues_stats':
            return self.snapshot_queues_stats()

    def snapshot_backend_info(self):
        return dict(
            backend_id=self.scheduler.backend.get_id(),
            backend_info=self.scheduler.backend.info(),
            backend_type=self.scheduler.backend.get_type(),
            timestamp=time.time()
        )

    def snapshot_queues_stats(self):
        stats = copy.copy(self._stats)
        self._reset_stats()
        config = {}
        for queue_id in stats:
            config[queue_id] = \
                self.scheduler.get_queue_config(queue_id)

        return dict(
            backend_id=self.scheduler.backend.get_id(),
            queues_config=config,
            queues_stats=stats,
            timestamp=time.time()
        )

    def snapshot_queues_info(self):
        return dict(
            backend_id=self.scheduler.backend.get_id(),
            queues_info=self.scheduler.backend.queues_info(),
            timestamp=time.time()
        )
