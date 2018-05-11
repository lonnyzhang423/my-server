import contextlib

import redis
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from config import Config

__all__ = ["init_db", "session_scope", "Model", "RedisCache"]


# noinspection PyUnresolvedReferences
def init_db():
    import db.models
    Model.metadata.create_all(_engine)


def init_redis():
    pool = redis.ConnectionPool(host="localhost", port=6379, db=0, decode_responses=True)
    return redis.Redis(connection_pool=pool)


@contextlib.contextmanager
def session_scope():
    sess = Session()
    try:
        yield sess
        sess.commit()
    except:
        sess.rollback()
        raise
    finally:
        sess.close()


RedisCache = init_redis()
_engine = engine_from_config(Config["database"])
_factory = sessionmaker(bind=_engine, expire_on_commit=False)
Session = scoped_session(_factory)
Model = declarative_base()
