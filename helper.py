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
from database.models import Admin


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
def load_admin_uids():
    try:
        with session_scope() as sess:
            targets = sess.query(Admin)
            return [admin.uid for admin in targets]
    except BaseException:
        return None


def login_required(func):
    """
    检查HTTP Header Authorization参数
    判断是否登录
    """

    # noinspection PyBroadException
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if isinstance(auth, str):
            try:
                token_type, access_token = auth.split(" ")
                uid = db.RedisCache.get(access_token)
            except BaseException:
                data = RespData(code=401, message="Unauthorized").to_json()
                return Response(status=401, response=data)

            if uid:
                kwargs["uid"] = uid
                kwargs["access_token"] = access_token
                return func(*args, **kwargs)

        data = RespData(code=401, message="Unauthorized").to_json()
        return Response(status=401, response=data)

    return wrapper


def admin_login_required(func):
    """
    检查Http header Authorization参数
    判断是否管理员登录
    """

    # noinspection PyBroadException
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if isinstance(auth, str):
            try:
                token_type, access_token = auth.split(" ")
                uid = db.RedisCache.get(access_token)
                uids = load_admin_uids()
                if uid not in uids:
                    raise Exception
            except BaseException:
                data = RespData(code=401, message="Unauthorized").to_json()
                return Response(status=401, response=data)

            if uid:
                kwargs["uid"] = uid
                kwargs["access_token"] = access_token
                return func(*args, **kwargs)

        data = RespData(code=401, message="Unauthorized").to_json()
        return Response(status=401, response=data)

    return wrapper


def get_logger(name, file, sl=logging.DEBUG, fl=logging.INFO):
    target = logging.getLogger(name)
    target.setLevel(logging.DEBUG)

    if not len(target.handlers):
        target.handlers.clear()

    curdir = os.path.abspath(os.path.dirname(__file__))
    curdir = os.path.join(curdir, "logs")
    if not os.path.exists(curdir):
        os.makedirs(curdir)
    logfile = os.path.join(curdir, file)

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


logger = get_logger("global_logger", "common.log")
