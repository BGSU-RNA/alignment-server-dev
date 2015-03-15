import abc
import uuid
import logging

import beanstalkc

import simplejson as json

from db.cache import Cache


KNOWN_STATUS = set(['pending', 'submitted', 'failed', 'succeeded'])
FINISHED_STATUS = set(['failed', 'suceeded'])


class MissingResults(Exception):
    """An exception that is thrown if we are missing a results file when we are
    asked for the results.
    """
    pass


class Queue(object):
    """This class represents a queue. This can submit something to the queue,
    determine the current status and get the result of processing. Jobs will be
    submitted to beanstalk, while the status and results will be fetched from
    the cache.
    """

    def __init__(self, config):
        self.cache = Cache(config)
        self.beanstalk = beanstalkc.Connection(**config['queue']['connection'])
        self.beanstalk.use(config['queue']['name'])
        self.beanstalk.ignore('default')

    def submit(self, query):
        self.beanstalk.put(json.dumps(query))
        data = dict(query)
        data['status'] = 'submitted'
        self.cache.set(query['id'], data)

    def status(self, query):
        info = self.cache.get(query['id'])
        status = info.get('status', None)
        if status is None or status not in KNOWN_STATUS:
            return 'unknown'
        return status

    def result(self, query):
        result = self.cache.get(query)
        if not result:
            raise MissingResults()
        return result


class Worker(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config, **kwargs):
        self.cache = Cache(config)
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
        self.cache.set(result['id'], info)

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
                self.save(query, status='failed')
                job.delete()
