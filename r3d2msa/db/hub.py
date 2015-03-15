from sqlalchemy import create_engine

from contextlib import contextmanager


class ProcessingException(Exception):
    """Raised when we can't process a range in the database.
    """
    pass



class Session(object):
    def __init__(self, builder):
        self.builder = builder

    @contextmanager
    def __call__(self):
        session = self.builder()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()
