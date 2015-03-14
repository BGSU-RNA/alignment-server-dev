import abc
import uuid
import logging

import beanstalkc

import simplejson as json

import db


class MissingResults(Exception):
    """An exception that is thrown if we are missing a results file when we are
    asked for the results.
    """
    pass


class Queue(object):
    known_status = set(['pending', 'submitted', 'failed', 'succeeded'])

    def __init__(self, config):
        self.engine = db.hub_connect(config)
        self.beanstalk = beanstalkc.Connection(**config['queue']['connection'])
        self.beanstalk.use(config['queue']['queue'])
        self.beanstalk.ignore('default')

    def submit(self, data):
        query = json.dump(data)
        job_id = self.beanstalk.put(query)
        db.mark_submitted(job_id, data)

    def status(self, data):
        status = db.job_status(data['id'])
        if status is None or status not in self.known_status:
            return 'unknown'
        return status

    def result(self, data):
        result = db.job

        if not result:
            raise MissingResults()

        return json.load(result)


class Worker(object):
    __metaclass__ = abc.MetaClass

    def __init__(self, config, **kwargs):
        self.engine = db.hub_connect(config)

        self.beanstalk = beanstalkc.Connection(**config['queue']['connection'])
        self.beanstalk.watch(config['queue']['queue'])
        self.beanstalk.ignore('default')

        self.uuid = str(uuid.uuid4())
        self.logger = logging.getLogger('queue.Worker:%s' % self.uuid)

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abc.abstractmethod
    def process(self, query):
        pass

    def save(self, job, query, result):
        job.delete()
        db.save_job(job.id, query, result)

    def failed(self, job, query):
        job.delete()
        db.failed_job(job.id, query)

    def __call__(self):
        while True:
            job = self.beanstalk.reserve()
            job.bury()
            try:
                query = json.load(job.body)
                result = self.process(query)
                self.save(query, result)
            except Exception as err:
                self.logger.exception(err)
                self.failed(job, query)
