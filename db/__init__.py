import functools

from flask import request, Response

from api import RespData
from db.wrapper import session, db

__all__ = ['db', 'session', 'login_required', 'admin_login_required']


# noinspection PyBroadException
@functools.lru_cache()
def load_admin_uids():
    try:
        from db.models import Admin
        with session() as sess:
            targets = sess.query(Admin)
            return [admin.uid for admin in targets]
    except BaseException:
        return None


def login_required(func):
    """
    判断是否普通用户登录
    """

    # noinspection PyBroadException
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if isinstance(auth, str):
            try:
                token_type, access_token = auth.split(" ")
                uid = db.Redis.get(access_token)
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
    判断是否管理员登录
    """

    # noinspection PyBroadException,PyShadowingNames
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if isinstance(auth, str):
            try:
                token_type, access_token = auth.split(" ")
                uid = db.Redis.get(access_token)
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
