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
    QUEUE_PREFIX = 'q'
    QUEUE_HASH_PREFIX = 'qh'
    WAITING_QUEUE_PREFIX = 'wq'
    TEMP_QUEUE_PREFIX = 'tempq'
    DEAD_LETTER_QUEUE_PREFIX = 'dlq'
    WAITING_SET_PREFIX = 'wn'
    QUEUE_LOCK_PREFIX = 'ql'

    def __init__(self, queue_id):
        self._queue_id = queue_id

    @property
    def queue_id(self):
        return self._queue_id

    @staticmethod
    def join(*args):
        return '::'.join(args) 

    def all_queue_hash_keys(self):
        return self.join(self.QUEUE_HASH_PREFIX, '*')

    def queue_key(self):
        return self.join(self.QUEUE_PREFIX, self._queue_id)

    def waiting_queue_key(self):
        return self.join(self.WAITING_QUEUE_PREFIX, self._queue_id)

    @classmethod
    def all_waiting_queue_keys(cls):
        return cls.join(cls.WAITING_QUEUE_PREFIX, '*')

    def queue_lock(self, *args):
        return self.join(self.QUEUE_LOCK_PREFIX, self._queue_id, *args)

    def task_lock(self, task_id):
        return self.queue_lock('task', task_id)

    def waiting_set_key(self):
        return self.join(self.WAITING_SET_PREFIX, self._queue_id)

    @staticmethod
    def waiting_id(task_id):
        return Namespace.join(str(ms_now()), task_id)

    def queue_hash_key(self):
        return self.join(self.QUEUE_HASH_PREFIX, self._queue_id)

    def dlq_key(self):
        return self.join(self.DEAD_LETTER_QUEUE_PREFIX, self._queue_id)

    @classmethod
    def all_temp_queue_keys(cls):
        return cls.join(cls.TEMP_QUEUE_PREFIX, '*')

    def temp_queue_key(self):
        return self.join(self.TEMP_QUEUE_PREFIX, self._queue_id, str(ms_now()), str(uuid4()))


class RedisBackend(BaseBackend):
    LOCK_TIMEOUT = 10  # seconds

    HANDLE_TIMEOUT_INTERVAL = 1000
    HANDLE_TEMP_INTERVAL = 10000

    def __init__(self, max_retry=5, timeout=30000, **kwargs):
        self.max_retry = max_retry
        self.timeout = timeout

        self._kwargs = kwargs
        self._connection = Connection(**self._kwargs)

        now = ms_now()
        self._last_handle_timeout = now
        self._last_handle_temp = now

        self._register_scripts()

    def _register_scripts(self):
        self._scripts = {
            'ack_task': self.client.register_script(
                # KEYS[1] queue_hash_key
                # KEYS[2] waiting_set_key
                # KEYS[3] task_id
                '''
                    if(redis.call('sismember', KEYS[2], KEYS[3]))
                    then
                        redis.call('hdel', KEYS[1], KEYS[3])
                        redis.call('srem', KEYS[2], KEYS[3])
                        return 1
                    end
                    return 0
                '''
            ),
            'reject_task': self.client.register_script(
                # KEYS[1] queue_hash_key
                # KEYS[2] waiting_set_key
                # KEYS[3] dlq_key
                # KEYS[4] task_id
                '''
                    local task_data = redis.call('hget', KEYS[1], KEYS[4])
                    if(task_data)
                    then
                        redis.call('hdel', KEYS[1], KEYS[4])
                        redis.call('srem', KEYS[2], KEYS[4])
                        redis.call('lpush', KEYS[3], task_data)
                        return 1
                    end
                    return 0
                '''
            ),
            'get_waiting_id': self.client.register_script(
                # KEYS[1] waiting_queue_key
                # KEYS[2] waiting_set_key
                '''
                    local waiting_id, timestamp, task_id
                    while(1) do
                        waiting_id = redis.call('lindex', KEYS[1], -1)
                        if(waiting_id)
                        then
                            timestamp, task_id = waiting_id:match('(.+)::(.+)')
                            if(redis.call('sismember', KEYS[2], task_id) == 1)
                            then
                                break
                            else
                                redis.call('rpop', KEYS[1])
                            end
                        else
                            break
                        end
                    end
                    return waiting_id
                '''
            )
        }

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

    def lock(self, lock_name):
        lock = self.client.set(lock_name, str(ms_now()), nx=True, ex=self.LOCK_TIMEOUT)
        return lock

    def handle_timeout(self):
        keys = self.client.keys(Namespace.all_waiting_queue_keys())
        for key in keys:
            key = key.decode()
            _, queue_id = key.split('::')
            namespace = Namespace(queue_id)
            queue_lock = namespace.queue_lock()
            if not self.lock(queue_lock):
                continue
            while self._handle_timeout(namespace):
                pass
            self.client.delete(queue_lock)

    def _handle_timeout(self, namespace):
        waiting_queue_key = namespace.waiting_queue_key()
        waiting_id = self._scripts['get_waiting_id'](
            keys=[waiting_queue_key,  namespace.waiting_set_key()]
        )
        if waiting_id is None:
            return False

        timestamp, task_id = waiting_id.decode().split('::')
        if float(timestamp) + self.timeout > ms_now():
            return False

        pipe = self.client.pipeline()
        self._nack_task_by_pipe(pipe, namespace, task_id)
        pipe.rpop(waiting_queue_key)
        pipe.execute()
        return True

    def handle_temp_queue(self):
        keys = self.client.keys(Namespace.all_temp_queue_keys())
        for key in keys:
            _, queue_id, timestamp, uniq = key.decode().split('::')
            if float(timestamp) + 10000 > ms_now():
                continue

            namespace = Namespace(queue_id)
            queue_lock = namespace.queue_lock('temp', uniq)

            if not self.lock(queue_lock):
                continue

            task_id = self.client.lindex(key, -1)
            if task_id is None:
                continue
            queue_key = namespace.queue_key()
            pipe = self.client.pipeline()
            pipe.rpush(queue_key, task_id)
            pipe.delete(key)
            pipe.delete(queue_lock)
            pipe.execute()

    @property
    def client(self):
        return self._connection.client

    def _safe_pop(self, queue_key, queue_id):
        namespace = Namespace(queue_id)
        temp_queue_key = namespace.temp_queue_key()
        task_id = self.client.rpoplpush(queue_key, temp_queue_key)
        if task_id:
            task_id = task_id.decode()
        return task_id, temp_queue_key

    def get_task(self, queue_id):
        namespace = Namespace(queue_id)
        queue_key = namespace.queue_key()
        task_id, temp_queue_key = self._safe_pop(queue_key, queue_id)
        if task_id is None:
            return None
        waiting_id = Namespace.waiting_id(task_id)

        pipe = self.client.pipeline()
        pipe.lpush(namespace.waiting_queue_key(), waiting_id)
        pipe.delete(temp_queue_key)
        pipe.sadd(namespace.waiting_set_key(), task_id)
        pipe.execute()

        task_data = self.client.hget(namespace.queue_hash_key(), task_id)
        task = unpack_task(task_data) if task_data else None
        return task

    def put_task(self, queue_id, task):
        task_id = str(uuid4())
        task['id'] = task_id
        task['meta']['retry'] = 0

        namespace = Namespace(queue_id)

        pipe = self.client.pipeline()
        pipe.hset(namespace.queue_hash_key(), task_id, pack_task(task))
        pipe.lpush(namespace.queue_key(), task_id)
        pipe.execute()
        return task_id

    def ack_task(self, queue_id, task_id):
        namespace = Namespace(queue_id)
        keys = [
            namespace.queue_hash_key(),
            namespace.waiting_set_key(),
            task_id
        ]
        return bool(self._scripts['ack_task'](keys=keys))

    def nack_task(self, queue_id, task_id):
        pipe = self.client.pipeline()
        r = self._nack_task_by_pipe(pipe, Namespace(queue_id), task_id)
        pipe.execute()
        return r

    def _nack_task_by_pipe(self, pipe, namespace, task_id):
        task_lock = namespace.task_lock(task_id) 
        if not self.lock(task_lock):
            return False
        pipe.delete(task_lock)

        queue_hash_key = namespace.queue_hash_key()
        waiting_set_key = namespace.waiting_set_key()

        p = self.client.pipeline()
        p.sismember(waiting_set_key, task_id)
        p.hget(queue_hash_key, task_id)
        is_waiting, task_data = p.execute()

        if not is_waiting or task_data is None:
            return False

        pipe.hdel(queue_hash_key, task_id)
        pipe.srem(waiting_set_key, task_id)

        task = unpack_task(task_data)
        if task['meta']['retry'] >= task['meta'].get('max_retry', self.max_retry):
            pipe.lpush(namespace.dlq_key(), task_data)
        else:
            new_task_id = str(uuid4())
            task['id'] = new_task_id
            task['meta']['retry'] += 1

            pipe.hset(queue_hash_key, new_task_id, pack_task(task))
            pipe.rpush(namespace.queue_key(), new_task_id)
        return True

    def reject_task(self, queue_id, task_id):
        namespace = Namespace(queue_id)
        keys = [
            namespace.queue_hash_key(),
            namespace.waiting_set_key(),
            namespace.dlq_key(),
            task_id
        ]
        return bool(self._scripts['reject_task'](keys=keys))

    def queue_info(self, queue_id):
        namespace = Namespace(queue_id)

        pipe = self.client.pipeline()
        pipe.llen(namespace.queue_key())
        pipe.hlen(namespace.queue_hash_key())
        pipe.llen(namespace.dlq_key())
        pipe.scard(namespace.waiting_set_key())
        r = pipe.execute()

        return dict(
            queue_length=r[0],
            queue_hash_length=r[1],
            dead_letter_queue_length=r[2],
            waiting_length=int(r[3] or 0)
        )

    def queues_info(self):
        self.check()
        keys = self.client.keys(Namespace.all_queue_hash_keys())
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
