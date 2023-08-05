from uuid import uuid4
import time

import redis

from .base import BaseBackend, pack_task, unpack_task


def ms_now():
    return time.time() * 1000


class Connection(object):
    def __init__(self, **kwargs):
        self._pool = redis.ConnectionPool(
            host=kwargs['host'],
            port=kwargs['port'],
            db=kwargs['db'],
            password=kwargs.get('password', None)
        )
        self._client = redis.StrictRedis(
            connection_pool=self._pool
        )

    @property
    def client(self):
        return self._client


class Namespace(object):
    QUEUE_PREFIX = 'q::'
    QUEUE_HASH_PREFIX = 'qh::'
    WAITING_QUEUE_PREFIX = 'wq::'
    TEMP_QUEUE_PREFIX = 'tempq::'
    DEAD_LETTER_QUEUE_PREFIX = 'dlq::'

    WAITING_NUMBER_PREFIX = 'wn::'
    QUEUE_LOCK_PREFIX = 'ql::'

    def all_queue_hash_keys(self):
        return self.QUEUE_HASH_PREFIX + '*'

    def queue_key(self, queue_id):
        return self.QUEUE_PREFIX + queue_id

    def waiting_queue_key(self, queue_id):
        return self.WAITING_QUEUE_PREFIX + queue_id

    def all_waiting_queue_keys(self):
        return self.WAITING_QUEUE_PREFIX + '*'

    def queue_lock(self, queue_id, uniq=None):
        key = self.QUEUE_LOCK_PREFIX + queue_id
        if uniq:
            key = key + '::' + uniq
        return key

    def waiting_number_key(self, queue_id):
        return self.WAITING_NUMBER_PREFIX + queue_id

    def waiting_id(self, task_id):
        return str(ms_now()) + '::' + task_id

    def queue_hash_key(self, queue_id):
        return self.QUEUE_HASH_PREFIX + queue_id

    def dlq_key(self, queue_id):
        return self.DEAD_LETTER_QUEUE_PREFIX + queue_id

    def all_temp_queue_keys(self):
        return self.TEMP_QUEUE_PREFIX + '*'

    def temp_queue_prefix(self, queue_id):
        return self.TEMP_QUEUE_PREFIX + queue_id + '::'

    def temp_queue_key(self, queue_id):
        return self.temp_queue_prefix(queue_id) + \
            str(ms_now()) + '::' + str(uuid4())


class RedisBackend(BaseBackend):
    QUEUE_LOCK_TIMEOUT = 10  # seconds

    HANDLE_TIMEOUT_INTERVAL = 1000
    HANDLE_TEMP_INTERVAL = 10000

    def __init__(self, max_retry=5, timeout=30000, **kwargs):
        self.max_retry = max_retry
        self.timeout = timeout

        self._kwargs = kwargs
        self._connection = Connection(**self._kwargs)
        self._namespace = Namespace()

        now = ms_now()
        self._last_handle_timeout = now
        self._last_handle_temp = now

    @classmethod
    def get_type(self):
        return 'redis'

    def check(self):
        now = ms_now()
        if now - self._last_handle_temp > self.HANDLE_TEMP_INTERVAL:
            self._last_handle_temp = now
            self.handle_temp_queue()
        if now - self._last_handle_timeout > self.HANDLE_TIMEOUT_INTERVAL:
            self._last_handle_timeout = now
            self.handle_timeout()

    def handle_timeout(self):
        keys = self.client.keys(self._namespace.all_waiting_queue_keys())
        for key in keys:
            key = key.decode()
            _, queue_id = key.split('::')
            queue_lock = self._namespace.queue_lock(queue_id)
            # 获取锁
            lock = self.client.set(queue_lock, 1, nx=True,
                                   ex=self.QUEUE_LOCK_TIMEOUT)
            if not lock:
                continue
            while self.__handle_timeout(queue_id, key):
                pass
            self.client.delete(queue_lock)

    def __handle_timeout(self, queue_id, waiting_queue_key):
        waiting_id = self.client.lindex(waiting_queue_key, -1)
        if waiting_id is None:
            return False

        timestamp, task_id = waiting_id.decode().split('::')
        if float(timestamp) + self.timeout > ms_now():
            return False

        pipe = self.client.pipeline()
        self._nack_task_by_pipe(pipe, queue_id, task_id)
        pipe.rpop(waiting_queue_key)
        pipe.execute()
        return True

    def handle_temp_queue(self):
        keys = self.client.keys(self._namespace.all_temp_queue_keys())
        for key in keys:
            _, queue_id, timestamp, uniq = key.decode().split('::')
            if float(timestamp) + 10000 > ms_now():
                continue

            queue_lock = self._namespace.queue_lock(queue_id, uniq)
            # 获取锁
            lock = self.client.set(queue_lock, 1, nx=True,
                                   ex=self.QUEUE_LOCK_TIMEOUT)
            if not lock:
                continue

            task_id = self.client.lindex(key, -1)
            if task_id is None:
                continue

            queue_key = self._namespace.queue_key(queue_id)

            pipe = self.client.pipeline()
            pipe.rpush(queue_key, task_id)
            pipe.delete(key)
            pipe.delete(queue_lock)
            pipe.execute()

    @property
    def client(self):
        return self._connection.client

    def _safe_pop(self, queue_key, queue_id):
        temp_queue_key = self._namespace.temp_queue_key(queue_id)
        task_id = self.client.rpoplpush(queue_key, temp_queue_key)
        if task_id:
            task_id = task_id.decode()
        return task_id, temp_queue_key

    def get_task(self, queue_id):
        queue_key = self._namespace.queue_key(queue_id)
        task_id, temp_queue_key = self._safe_pop(queue_key, queue_id)
        if task_id is None:
            return None
        waiting_queue_key = self._namespace.waiting_queue_key(queue_id)
        waiting_number_key = self._namespace.waiting_number_key(queue_id)
        waiting_id = self._namespace.waiting_id(task_id)
        queue_hash_key = self._namespace.queue_hash_key(queue_id)

        pipe = self.client.pipeline()
        pipe.lpush(waiting_queue_key, waiting_id)
        pipe.delete(temp_queue_key)
        pipe.incr(waiting_number_key)
        pipe.execute()

        task_data = self.client.hget(queue_hash_key, task_id)
        task = unpack_task(task_data) if task_data else None
        return task

    def put_task(self, queue_id, task):
        task_id = str(uuid4())
        task['id'] = task_id
        task['meta']['retry'] = 0

        queue_hash_key = self._namespace.queue_hash_key(queue_id)
        queue_key = self._namespace.queue_key(queue_id)

        pipe = self.client.pipeline()
        pipe.hset(queue_hash_key, task_id, pack_task(task))
        pipe.lpush(queue_key, task_id)
        pipe.execute()
        return task_id

    def ack_task(self, queue_id, task_id):
        queue_hash_key = self._namespace.queue_hash_key(queue_id)

        if self.client.hexists(queue_hash_key, task_id):
            waiting_number_key = self._namespace.waiting_number_key(queue_id)

            pipe = self.client.pipeline()
            pipe.hdel(queue_hash_key, task_id)
            pipe.decr(waiting_number_key)
            pipe.execute()
            return True

        return False

    def nack_task(self, queue_id, task_id):
        pipe = self.client.pipeline()
        if self._nack_task_by_pipe(pipe, queue_id, task_id):
            pipe.execute()
            return True

        return False

    def _nack_task_by_pipe(self, pipe, queue_id, task_id):
        queue_hash_key = self._namespace.queue_hash_key(queue_id)
        task_data = self.client.hget(queue_hash_key, task_id)

        if task_data:
            task = unpack_task(task_data)
            if task['meta']['retry'] >= task['meta'].get('max_retry', self.max_retry):
                return self._reject_task_by_pipe(pipe, queue_id,
                                                 task_id, task_data)

            new_task_id = str(uuid4())
            task['id'] = new_task_id
            task['meta']['retry'] += 1

            queue_key = self._namespace.queue_key(queue_id)
            waiting_number_key = self._namespace.waiting_number_key(queue_id)

            pipe.hdel(queue_hash_key, task_id)
            pipe.decr(waiting_number_key)
            pipe.hset(queue_hash_key, new_task_id, pack_task(task))
            pipe.rpush(queue_key, new_task_id)
            return True

        return False

    def reject_task(self, queue_id, task_id):
        pipe = self.client.pipeline()
        if self._reject_task_by_pipe(pipe, queue_id, task_id):
            pipe.execute()
            return True

    def _reject_task_by_pipe(self, pipe, queue_id, task_id, task_data=None):
        queue_hash_key = self._namespace.queue_hash_key(queue_id)
        if task_data is None:
            task_data = self.client.hget(queue_hash_key, task_id)

        if task_data:
            dlq_key = self._namespace.dlq_key(queue_id)
            waiting_number_key = self._namespace.waiting_number_key(queue_id)

            pipe.hdel(queue_hash_key, task_id)
            pipe.decr(waiting_number_key)
            pipe.lpush(dlq_key, task_data)
            return True

    def queue_info(self, queue_id):
        queue_key = self._namespace.queue_key(queue_id)
        queue_hash_key = self._namespace.queue_hash_key(queue_id)
        dlq_key = self._namespace.dlq_key(queue_id)
        waiting_number_key = self._namespace.waiting_number_key(queue_id)

        pipe = self.client.pipeline()
        pipe.llen(queue_key)
        pipe.hlen(queue_hash_key)
        pipe.llen(dlq_key)
        pipe.get(waiting_number_key)
        r = pipe.execute()

        return dict(
            queue_length=r[0],
            queue_hash_length=r[1],
            dead_letter_queue_length=r[2],
            waiting_length=int(r[3] or 0)
        )

    def queues_info(self):
        self.check()
        all_queue_hash_keys = self._namespace.all_queue_hash_keys()
        keys = self.client.keys(all_queue_hash_keys)
        info = {}
        for key in keys:
            _, queue_id = key.decode().split('::')
            info[queue_id] = self.queue_info(queue_id)
        return info

    def info(self):
        return self.client.info()

    @classmethod
    def gen_id(cls, kwargs):
        s = '{}_{}_{}_{}'.format(cls.get_type(),
                                 kwargs["host"],
                                 kwargs['port'],
                                 kwargs['db'])
        return cls.sha256(s)

    def get_id(self):
        return self.gen_id(self._kwargs)
