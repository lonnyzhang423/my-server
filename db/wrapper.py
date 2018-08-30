import contextlib

import redis
from sqlalchemy import orm, engine_from_config

from config import Config

__all__ = ["db", "session"]


@contextlib.contextmanager
def session():
    """
    Provide a transactional scope around a series of operations
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
        from db.models import Model
        Model.metadata.create_all(self._engine)

    @staticmethod
    def init_redis():
        pool = redis.ConnectionPool(**Config["redis"])
        return redis.Redis(connection_pool=pool)


db = SqlAlchemy()
