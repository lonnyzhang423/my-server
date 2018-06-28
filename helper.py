import functools
import hashlib
import hmac
import logging
import logging.handlers
import os
import re
import uuid

from flask import request, Response

from api import RespData
from config import Config
from database import db, session_scope
from database.models import Oauth


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


def encrypt_password(password, salt):
    if isinstance(password, str):
        password = password.encode("utf8")
    if isinstance(salt, str):
        salt = salt.encode("utf8")
    return hmac.new(salt, password, hashlib.sha256).hexdigest()


def timestamp():
    import time
    return int(time.time() * 1000)


# noinspection PyBroadException
@functools.lru_cache()
def get_app_secret(app_id):
    try:
        with session_scope() as sess:
            target = sess.query(Oauth).filter(Oauth.app_id == app_id).first()
            return target.app_secret
    except BaseException:
        return None


# noinspection PyBroadException
def valid_app_id(app_id):
    return get_app_secret(app_id) is not None


# noinspection PyBroadException
def valid_nonce(nonce):
    try:
        exists = db.RedisCache.exists(nonce)
        gap = Config["request_gap_between_cs"]
        db.RedisCache.set(nonce, nonce, ex=gap // 1000)
        return not exists
    except BaseException:
        return False


# noinspection PyBroadException
def valid_timestamp(ts):
    try:
        max_ts_gap = Config["request_gap_between_cs"]
        sts = timestamp()
        cts = int(ts)
        return (sts - cts) < max_ts_gap
    except BaseException:
        return False


# noinspection PyBroadException
def valid_signature(app_id, timestamp, nonce, method, path, sig):
    try:
        app_secret = get_app_secret(app_id).encode("utf8")
        msg = (method + path + "?app_id=" + app_id +
               "&nonce=" + nonce +
               "&timestamp=" + str(timestamp)).encode("utf8")
        correct_sig = hmac.new(app_secret, msg, hashlib.sha256).hexdigest()
        if sig.lower() == correct_sig.lower():
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
                uid = db.RedisCache.get(access_token)
                if uid:
                    kwargs["uid"] = uid
                    kwargs["access_token"] = access_token
                    return func(*args, **kwargs)
        except (ValueError, AttributeError):
            pass
        data = RespData(code=401, message="Unauthorized").to_json()
        return Response(status=401, response=data)

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
    fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=Config["log_file_max_bytes"],
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
