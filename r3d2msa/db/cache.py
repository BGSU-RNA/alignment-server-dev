import simplejson as json

from sqlalchemy import MetaData
from sqlalchemy.sql import select
from sqlalchemy import create_engine


class Cache(object):
    def __init__(self, config):
        self.engine = create_engine(config['cache']['connection'])
        self.transaction = self.engine.begin
        meta = MetaData()
        meta.reflect(bind=self.engine)
        self.cache = meta.tables['cache']

    def get(self, query_id):
        with self.transaction() as connection:
            query = select([self.cache]).where(self.cache.c.id == query_id)
            result = connection.execute(query)
            result = result.first()

        if not result:
            return {}

        return json.loads(result['body'])

    def set(self, query_id, result):
        data = self.get(query_id)
        if data:
            query = self.cache.update()
        query = self.cache.insert()

        body = json.dumps(result)
        with self.transaction() as connection:
            query = query.values(id=query_id, body=body)
            connection.execute(query)
