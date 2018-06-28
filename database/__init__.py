import contextlib

import redis
from sqlalchemy import orm, engine_from_config
from sqlalchemy.ext.declarative import declarative_base

from config import Config

__all__ = ["db", "session_scope"]


@contextlib.contextmanager
def session_scope():
    sess = db.Session()
    try:
        yield sess
        sess.commit()
    except:
        sess.rollback()
        raise
    finally:
        sess.close()


class SqlAlchemy:

    def __init__(self):
        self._engine = engine_from_config(Config["database"])
        self._session_factory = orm.sessionmaker(bind=self._engine, expire_on_commit=False)
        self.Session = self._create_scoped_session()
        self.RedisCache = self._redis_cache()
        self.Model = declarative_base()

    # noinspection PyUnresolvedReferences
    def init_tables(self):
        import database.models
        self.Model.metadata.create_all(self._engine)

    @staticmethod
    def _redis_cache():
        pool = redis.ConnectionPool(host="localhost", port=6379, decode_responses=True)
        return redis.Redis(connection_pool=pool)

    def _create_scoped_session(self):
        return orm.scoped_session(session_factory=self._session_factory)


db = SqlAlchemy()
