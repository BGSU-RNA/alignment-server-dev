"""This module contains an abstract base class for all workers. It will handle
the logic of logging, queueing and caching, leaving only the actual processing
for subclasses to worry about.
"""

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
        """Create a new Worker. This uses the config dictionary to connect to
        the queue and worker. That dictionary must contain a cache dictionary
        with the keys connection to indicate the connection to use, timeout for
        the time in seconds until an object is expired in the cache.

        :config: A configuration dictionary. This must specify the cache and
        queue to use.
        :kwargs: Keyword arguments to set as attributes of this worker. If no
        name is given then a random UUID is generated as a name.
        """
        self.config = dict(config)
        self.cache = redis.Redis(**config['cache']['connection'])
        self.timeout = config['cache']['timeout']
        self.persist = set(config['cache'].get('persist', []))

        self.beanstalk = beanstalkc.Connection(**config['queue']['connection'])
        self.beanstalk.watch(config['queue']['name'])
        self.beanstalk.ignore('default')

        self.name = kwargs.get('name', str(uuid.uuid4()))
        self.logger = logging.getLogger('queue.Worker:%s' % self.name)

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abc.abstractmethod
    def process(self, query):
        """Process the data. This method takes the input query which was placed
        in the queue and preforms some operation to create the result data
        structure. That structure will be placed into the cache as needed. In
        addition, the state of the job will be updated. If this process fails
        it should raise an exception to indicate failure. All worker subclasses
        must implement this.

        :query: The query to process.
        :returns: The result.
        """
        pass

    def save(self, result, status='failed'):
        """Save an object into the cache. This will set the object, with
        whatever is in result['id'] to the new object and update it's status as
        well. If the object's id is not in self.persist then it will be given
        the lifetime set in self.timeout.

        :param dict result: The result dictionary to save.
        :param string status: The status to set.
        """

        self.logger.debug("Updating results for %s", result['id'])
        info = dict(result)
        info['status'] = status
        self.cache.set(info['id'], json.dumps(info, separators=(',', ':')))

        if info['id'] not in self.persist:
            self.cache.expire(info['id'], self.timeout)

    def work(self, job, query):
        """Work on a job. This will work on some job until it is finished. The
        job will be deleted from the queue if this finishes. The job's status
        will be set to pending while it is being processed and then to success
        if it succeeds.

        :param Job job: The job to work on.
        :param dict query: The query to work on.
        """

        self.logger.debug("Working on query %s", query['id'])
        self.save(query, status='pending')
        result = self.process(query)
        self.logger.debug("Done working on %s", query['id'])
        self.save(result, status='succeeded')
        job.delete()

    def __call__(self):
        """The main entry point for all workers. When called this will wait
        until a job can be reserved from the queue and then send it to
        self.work(). The jobs body's are expected to be JSON encoded
        dictionaries. Results from processing are saved as JSON encoded objects
        into the cache.
        """

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
