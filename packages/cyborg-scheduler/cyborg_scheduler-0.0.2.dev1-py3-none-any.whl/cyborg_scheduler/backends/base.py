from abc import ABCMeta, abstractmethod
import hashlib
import json
import copy

from suitcase.structure import Structure
from suitcase.fields import LengthField, UBInt64, VariableRawPayload, Payload


class BaseBackend(metaclass=ABCMeta):
    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def put_task(self, queue_id, task):
        pass

    @abstractmethod
    def get_task(self, queue_id):
        pass

    @abstractmethod
    def ack_task(self, queue_id, task_id):
        pass

    @abstractmethod
    def nack_task(self, queue_id, task_id):
        pass

    @abstractmethod
    def reject_task(self, queue_id, task_id):
        pass

    @abstractmethod
    def queue_info(self, queue_id):
        pass

    @abstractmethod
    def queues_info(self):
        pass

    @abstractmethod
    def info(self):
        pass

    def get_id(self):
        return self.gen_id(self._kwargs)

    @classmethod
    @abstractmethod
    def gen_id(kwargs):
        pass

    @classmethod
    @abstractmethod
    def get_type(cls):
        pass

    @staticmethod
    def sha256(s):
        return hashlib.sha256(s.encode()).hexdigest()


class TaskMessage(Structure):
    id_length = LengthField(UBInt64())
    id = VariableRawPayload(id_length)
    meta_length = LengthField(UBInt64())
    meta = VariableRawPayload(meta_length)
    body = Payload()


def pack_task(task):
    task_msg = TaskMessage()
    task_msg.id = task['id'].encode()

    meta = copy.copy(task['meta'])
    body = task['body']
    meta['body_type'] = 'bytes'
    if type(body) is dict:
        meta['body_type'] = 'dict'
        body = json.dumps(body).encode()
    elif type(body) is list:
        meta['body_type'] = 'list'
        body = json.dumps(body).encode()
    elif type(body) is tuple:
        meta['task_body'] = 'tuple'
        body = json.dumps(body).encode()
    elif type(body) is str:
        meta['body_type'] = 'str'
        body = body.encode()
    elif type(body) is int:
        meta['body_type'] = 'int'
        body = str(body).encode()
    elif type(body) is float:
        meta['body_type'] = 'float'
        body = str(body).encode()

    task_msg.body = body
    task_msg.meta = json.dumps(meta).encode()
    return task_msg.pack()


def unpack_task(data):
    task_msg = TaskMessage()
    task_msg.unpack(data)
    task = dict(
        id=task_msg.id.decode(),
        meta=json.loads(task_msg.meta.decode()),
    )

    meta = task['meta']
    body = task_msg.body
    body_type = meta['body_type']
    if body_type == 'dict':
        body = json.loads(body.decode())
    elif body_type == 'list':
        body = json.loads(body.decode())
    elif body_type == 'tuple':
        body = tuple(json.loads(body.decode()))
    elif body_type == 'str':
        body = body.decode()
    elif body_type == 'int':
        body = int(body.decode())
    elif body_type == 'float':
        body = int(body.decode())

    task['body'] = body
    return task

