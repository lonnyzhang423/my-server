import contextlib
import json
import os

import redis
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

__all__ = ["init_db", "session_scope", "Model", "RedisCache"]


# noinspection PyUnresolvedReferences
def init_db():
    import db.models
    Model.metadata.create_all(_engine)


def init_redis():
    pool = redis.ConnectionPool(host="localhost", port=6379, db=0, decode_responses=True)
    return redis.Redis(connection_pool=pool)


def _load_config():
    parent = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    target = os.path.join(parent, "config.json")
    with open(target, encoding="utf8") as f:
        config = json.load(f)
    return config["database"]


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
_engine = engine_from_config(_load_config())
_factory = sessionmaker(bind=_engine, expire_on_commit=False)
Session = scoped_session(_factory)
Model = declarative_base()
