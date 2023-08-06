# fork from:
# https://github.com/binux/pyspider/blob/master/pyspider/scheduler/token_bucket.py

import time
try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading


class Bucket(object):

    '''
    traffic flow control with token bucket
    '''

    update_interval = 30

    def __init__(self, rate=1, burst=None):
        self.rate = float(rate)
        if burst is None:
            self.burst = float(rate) * 10
        else:
            self.burst = float(burst)
        self.mutex = _threading.Lock()
        self.bucket = self.burst
        self.last_update = time.time()

    def get(self):
        '''Get the number of tokens in bucket'''
        now = time.time()
        if self.bucket >= self.burst:
            self.last_update = now
            return self.bucket
        bucket = self.rate * (now - self.last_update)
        self.mutex.acquire()
        if bucket > 1:
            self.bucket += bucket
            if self.bucket > self.burst:
                self.bucket = self.burst
            self.last_update = now
        self.mutex.release()
        return self.bucket

    def set(self, value):
        '''Set number of tokens in bucket'''
        self.bucket = value

    def desc(self, value=1):
        '''Use value tokens'''
        self.bucket -= value
