import redis
import simplejson as json


class Queue(object):
    """This class represents a queue. This can submit something to the queue,
    determine the current status and get the result of processing. Jobs will be
    submitted to beanstalk, while the status and results will be fetched from
    the cache.
    """

    def __init__(self, config):
        self.cache = redis.StrictRedis(**config['cache']['connection'])
        self.timeout = config['cache']['timeout']

    def put(self,

    def submit(self, query):
        data = dict(query)
        data['status'] = 'submitted'
        body = json.dumps(data)
        self.beanstalk.put(body)
        self.cache.set(query['id'], body)
        self.cache.expire(query['id'], self.timeout)
        return data

    def process(self, query):
        result = self.cache.get(query['id'])
        if not result:
            return self.submit(query)
        return result

