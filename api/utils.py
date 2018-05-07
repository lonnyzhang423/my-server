import functools
import hashlib
import hmac
import logging
import logging.handlers
import os
import re
import uuid

from flask import request

from db.database import RedisCache, session_scope
from db.models import Oauth, Response

__all__ = ["salt_from_uid", "random_token", "random_uid", "valid_app_id", "valid_signature",
           "login_required", "valid_timestamp", "valid_phone", "valid_password", "common_logger",
           "logger", "timestamp"]


def salt_from_uid(uid):
    return uid[-8:]


def random_token():
    return str(uuid.uuid4())


def random_uid():
    return uuid.uuid4().hex


def valid_phone(num):
    if not num:
        return False
    return False if len(num) is not 11 else re.match("1\d{10}", num) is not None


def valid_password(pwd):
    if not pwd:
        return False
    return True if len(pwd) >= 8 else False


def timestamp():
    import time
    return int(time.time() * 1000)


oauth = dict()


# noinspection PyBroadException
def valid_app_id(app_id):
    try:
        if app_id not in oauth:
            with session_scope() as sess:
                target = sess.query(Oauth).filter(Oauth.app_id == app_id).first()
                if target:
                    oauth[target.app_id] = target.app_secret
        return app_id in oauth
    except BaseException:
        return False


# noinspection PyBroadException
def valid_timestamp(ts):
    try:
        max_ts_gap = 1000 * 60 * 60 * 12
        sts = timestamp()
        cts = int(ts)
        return (sts - cts) < max_ts_gap
    except BaseException:
        return False


# noinspection PyBroadException
def valid_signature(app_id, timestamp, method, path, sig):
    try:
        app_secret = oauth.get(app_id).encode("utf8")
        msg = (method + path + "?app_id=" + app_id + "&timestamp=" + str(timestamp)).encode("utf8")
        correct_sig = hmac.new(app_secret, msg, hashlib.sha256).hexdigest()
        if sig == correct_sig:
            return True
        else:
            return False
    except BaseException:
        return False


def login_required(func):
    """
    检查HTTP Header Authorization参数
    判断是否登录
    """

    # noinspection PyBroadException
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            auth = request.headers.get("Authorization")
            if auth and isinstance(auth, str):

                token_type, access_token = auth.split(" ")
                uid = RedisCache.get(access_token)
                if uid:
                    kwargs["uid"] = uid
                    kwargs["access_token"] = access_token
                    return func(*args, **kwargs)
        except (ValueError, AttributeError):
            pass
        return Response.e_401().to_json(), 401

    return wrapper


def common_logger(name, file, sl=logging.DEBUG, fl=logging.INFO):
    target = logging.getLogger(name)
    target.setLevel(logging.DEBUG)

    if not len(target.handlers):
        target.handlers.clear()

    pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    logdir = os.path.join(pardir, "logs")
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    logfile = os.path.join(logdir, file)

    # 100MB
    fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=1024 * 1024 * 100,
                                              encoding="utf8", backupCount=2)
    sh = logging.StreamHandler()

    fmt = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(fmt=fmt)
    sh.setFormatter(fmt=fmt)
    fh.setLevel(fl)
    sh.setLevel(sl)

    target.addHandler(sh)
    target.addHandler(fh)

    return target


logger = common_logger("global_logger", "common.log")
