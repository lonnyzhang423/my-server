import contextlib

import redis
from sqlalchemy import orm, engine_from_config

from config import Config
from db.models import *

__all__ = ["db", "session"]


@contextlib.contextmanager
def session():
    """
    数据库会话
    """
    s = db.Session()
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()


class SqlAlchemy(object):
    """
    数据库包装类
    """

    def __init__(self):
        self._engine = engine_from_config(Config["database"])
        self._session_factory = orm.sessionmaker(bind=self._engine, expire_on_commit=False)
        self.Session = orm.scoped_session(session_factory=self._session_factory)
        self.Redis = self.init_redis()

    def init_tables(self):
        Model.metadata.create_all(self._engine)

    @staticmethod
    def init_redis():
        pool = redis.ConnectionPool(host="localhost", port=6379, decode_responses=True)
        return redis.Redis(connection_pool=pool)


db = SqlAlchemy()
