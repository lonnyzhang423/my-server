import contextlib

import redis
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

__all__ = ["init_db", "session_scope", "Model", "RedisCache"]

config = {
    "sqlalchemy.url": "mysql+mysqlconnector://user:password@localhost:3306/my_server",
    "sqlalchemy.echo": True
}

_engine = engine_from_config(config)
_factory = sessionmaker(bind=_engine, expire_on_commit=False)
Session = scoped_session(_factory)
Model = declarative_base()

_pool = redis.ConnectionPool(host="localhost", port=6379, db=0, decode_responses=True)
RedisCache = redis.Redis(connection_pool=_pool)


# noinspection PyUnresolvedReferences
def init_db():
    import db.models
    Model.metadata.create_all(_engine)


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
