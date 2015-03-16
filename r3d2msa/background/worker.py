import abc
import uuid
import logging

import redis
import beanstalkc
import simplejson as json


class Worker(object):
    """A base class for background workers. This provides the basic logic for
    getting jobs from beanstalk and storing them in the cache as needed. This
    has a process() method which should implement the needed processing steps.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, config, **kwargs):
        self.cache = redis.StrictRedis(**config['cache']['connection'])
        self.timeout = config['cache']['timeout']
        self.presist = set(config['cache'].get('persist', []))

        self.beanstalk = beanstalkc.Connection(**config['queue']['connection'])
        self.beanstalk.watch(config['queue']['name'])
        self.beanstalk.ignore('default')

        self.name = kwargs.get('name', str(uuid.uuid4()))
        self.logger = logging.getLogger('queue.Worker:%s' % self.name)

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abc.abstractmethod
    def process(self, query):
        pass

    def save(self, result, status='failed'):
        self.logger.debug("Updating results for %s", result['id'])
        info = dict(result)
        info['status'] = status
        self.cache.set(info['id'], json.dumps(info, separators=(',', ':')))

        if info['id'] not in self.presist:
            self.cache.expire(info['id'], self.timeout)

    def work(self, job, query):
        self.logger.debug("Working on query %s", query['id'])
        self.save(query, status='pending')
        result = self.process(query)
        self.logger.debug("Done working on %s", query['id'])
        self.save(result, status='succeeded')
        job.delete()

    def __call__(self):
        self.logger.info("Starting worker %s", self.name)
        while True:
            job = self.beanstalk.reserve()
            job.bury()
            try:
                query = json.loads(job.body)
                self.work(job, query)
            except Exception as err:
                self.logger.error("Error working with %s", query['id'])
                self.logger.exception(err)
                query['reason'] = 'Server Error'
                self.save(query, status='failed')
                job.delete()
