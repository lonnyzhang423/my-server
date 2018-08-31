import hashlib
import hmac
import logging
import logging.handlers
import os
import re
import uuid

from db import login_required, admin_login_required

__all__ = ['login_required', 'admin_login_required',
           'salt_from_uid', 'random_token', 'random_uid',
           'check_phone_num', 'check_password', 'encrypt_password',
           'get_logger', 'log_dir', 'logger']


def salt_from_uid(uid):
    return uid[-8:]


def random_token():
    return str(uuid.uuid4())


def random_uid():
    return uuid.uuid4().hex


def check_phone_num(num):
    """
    检查是否合法手机号
    """
    if not num:
        return False
    return False if len(num) is not 11 else re.match("1\d{10}", num) is not None


def check_password(pwd):
    """
    检查是否合法密码
    """
    if not pwd:
        return False
    return True if len(pwd) >= 8 else False


def encrypt_password(password, salt):
    """
    密码加密
    :param password: 明文密码
    :param salt: 盐
    :return: 加密字符串
    """
    if isinstance(password, str):
        password = password.encode("utf8")
    if isinstance(salt, str):
        salt = salt.encode("utf8")
    return hmac.new(salt, password, hashlib.sha256).hexdigest()


def get_logger(name="global_logger", file="common.log", sl=logging.DEBUG, fl=logging.INFO):
    """
    :param name: 唯一标识
    :param file: 日志文件名称
    :param sl: 控制台日志级别
    :param fl: 文件日志级别
    :return:日志记录器
    """

    target = logging.getLogger(name)
    target.setLevel(logging.DEBUG)

    if not len(target.handlers):
        target.handlers.clear()

    logfile = os.path.join(log_dir(), file)

    # 100MB
    fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=100 * 1024 * 1024, encoding="utf8", backupCount=2)
    sh = logging.StreamHandler()

    fmt = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(fmt=fmt)
    sh.setFormatter(fmt=fmt)
    fh.setLevel(fl)
    sh.setLevel(sl)

    target.addHandler(sh)
    target.addHandler(fh)

    return target


def log_dir():
    """
    :return: 日志目录
    """
    curdir = os.path.abspath(os.path.dirname(__file__))
    logdir = os.path.join(curdir, "logs")
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    return logdir


logger = get_logger()
