from flask import request

import helper
from api import *
from config import *
from db.database import RedisCache, session_scope
from db.models import *

__all__ = ["RegisterApi", "LoginApi", "LogoutApi", "SelfApi", "PasswordApi"]


class RegisterApi(BaseMethodView):
    # 注册类型
    RT = ("phone",)

    # noinspection PyBroadException
    def post(self):
        """
        注册
        """
        params = request.form
        rt = params.get("register_type")
        username = params.get("username")
        password = params.get("password")

        if rt not in self.RT:
            if rt is None:
                data = RespData(code=400, message="register_type required").to_json()
            else:
                data = RespData(code=400, message="unsupported register_type:{}".format(rt)).to_json()
            return MyResponse(response=data)

        if not helper.valid_phone(username):
            data = RespData(code=400, message="illegal phone num").to_json()
            return MyResponse(response=data)

        if not helper.valid_password(password):
            data = RespData(code=400, message="illegal password").to_json()
            return MyResponse(response=data)

        with session_scope() as session:
            ua = session.query(UserAuth).filter(UserAuth.username == username).first()
            if ua:
                data = RespData(code=400, message="username:{} already exists".format(username)).to_json()
                return MyResponse(response=data)

            uid = helper.random_uid()
            salt = helper.salt_from_uid(uid)
            encrypted = helper.encrypt_password(password, salt)

            user = User(uid=uid)
            user_auth = UserAuth(uid=uid, register_type=rt, username=username, password=encrypted)
            session.add(user)
            session.add(user_auth)
        data = RespData(code=200, message="register success", data={"uid": uid}).to_json()
        return MyResponse(response=data)


class LoginApi(BaseMethodView):
    def post(self):
        """
        登录
        """
        params = request.form
        gt = params.get("login_type")
        username = params.get("username")
        password = params.get("password")

        if gt not in RegisterApi.RT:
            if gt is None:
                data = RespData(code=400, message="register_type required").to_json()
            else:
                data = RespData(code=400, message="unsupported login_type:{}".format(gt)).to_json()
            return MyResponse(response=data)

        if not helper.valid_phone(username):
            data = RespData(code=400, message="illegal phone num").to_json()
            return MyResponse(response=data)

        if not helper.valid_password(password):
            data = RespData(code=400, message="illegal password").to_json()
            return MyResponse(response=data)

        with session_scope() as session:
            ua = session.query(UserAuth).filter(UserAuth.username == username).first()
            if ua is None:
                data = RespData(code=400, message="username or password is wrong").to_json()
                return MyResponse(response=data)

        uid = ua.uid
        correct = ua.password

        salt = helper.salt_from_uid(uid)
        encrypted = helper.encrypt_password(password, salt)

        if encrypted != correct:
            data = RespData(code=400, message="username or password is wrong").to_json()
            return MyResponse(response=data)

        token = helper.random_token()
        expires_in = Config["token_expires_in_ms"]
        RedisCache.set(name=token, value=uid, ex=expires_in // 1000)

        data = RespData(code=200, message="login success",
                        data={"uid": uid, "access_token": token, "token_type": "Bearer",
                              "expires_in": expires_in}).to_json()
        return MyResponse(response=data)


class LogoutApi(BaseMethodView):

    @helper.login_required
    def post(self, uid=None, access_token=None):
        """
        退出登录
        """
        params = request.form

        RedisCache.delete(access_token)
        data = RespData(code=200, message="logout success uid:{}".format(uid)).to_json()
        return MyResponse(response=data)


# noinspection PyMethodMayBeStatic
class SelfApi(BaseMethodView):

    @helper.login_required
    def get(self, uid=None, access_token=None):
        """
        获取个人信息
        """
        params = request.args

        with session_scope() as session:
            target = session.query(User).filter(User.uid == uid).first()
            if target:
                data = RespData(code=200, data=target.to_dict()).to_json()
                return MyResponse(response=data)
            else:
                data = RespData(code=500, message="Internal Server Error").to_json()
                return MyResponse(status=500, response=data)

    @helper.login_required
    def put(self, uid=None, access_token=None):
        """
        更新个人信息
        """
        params = request.form
        nickname = params.get("nickname")
        gender = params.get("gender")
        headline = params.get("headline")

        if not uid:
            data = RespData(code=401, message="access_token is invalid or out of date").to_json()
            return MyResponse(status=401, response=data)

        with session_scope() as session:
            target = session.query(User).filter(User.uid == uid).first()
            if target:
                target.nickname = nickname
                target.gender = gender
                target.headline = headline
                data = RespData(code=200, message="update success", data=target.to_dict()).to_json()
                return MyResponse(response=data)
            else:
                data = RespData(code=500, message="Internal Server Error").to_json()
                return MyResponse(status=500, response=data)


class PasswordApi(BaseMethodView):

    def put(self):
        pass
