"""This module contains a generic queue class. It is meant to serve as simple
way to connect to some beanstalk queue and place jobs. This can place things
into the queue and update the status in the cache.
"""

import redis
import beanstalkc
import simplejson as json


class Queue(object):
    """This class represents a queue. This can submit something to the queue,
    determine the current status and get the result of processing. Jobs will be
    submitted to beanstalk, while the status and results will be fetched from
    the cache.
    """

    def __init__(self, config):
        """Create a new Queue. The config dictionary must contain a queue
        dictonary with a connection and name entry that indicates the
        connection to use for beanstalk and the name of the beanstalk tube to
        use. The default tube will be ignored.
        """

        self.cache = redis.StrictRedis(**config['cache']['connection'])
        self.beanstalk = beanstalkc.Connection(**config['queue']['connection'])
        self.beanstalk.use(config['queue']['name'])
        self.beanstalk.ignore('default')

    def _submit(self, query):
        """Submit a job to the queue. It will be placed in the queue as well as
        the cache with the status set to 'submitted'.

        :param dict query: The query to process.
        """

        data = dict(query)
        data['status'] = 'submitted'
        body = json.dumps(data, separators=(',', ':'))
        self.beanstalk.put(body)
        self.cache.set(query['id'], body)
        return data

    def process(self, query):
        """Process a job. This is the main entry point for all queue related
        jobs. Users of this class should give a job to process to query. It
        will return the current status of the job. If it is finished then the
        completed object will be returned otherwise some object with a status
        meaning incomplete will be returned. If the job is unknown then it will
        be placed in the queue for processing.

        :param dict query: The query to process.
        :returns: The current result of this job.
        """

        result = self.cache.get(query['id'])
        if not result:
            return self._submit(query)
        return json.loads(result)
