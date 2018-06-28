from flask import request

import helper
from api import *
from config import *
from database import db, session_scope

__all__ = ["RegisterApi", "LoginApi", "LogoutApi"]


class RegisterApi(BaseMethodView):
    # noinspection PyBroadException
    def post(self):
        """
        注册
        """
        params = request.form
        username = params.get("name")
        password = params.get("password")

        with session_scope() as session:
            ua = session.query(Admin).filter(Admin.username == username).first()
            if ua:
                data = RespData(code=400, message="用户名:{}已存在".format(username)).to_json()
                return MyResponse(response=data)

            uid = helper.random_uid()
            salt = helper.salt_from_uid(uid)
            encrypted = helper.encrypt_password(password, salt)

            admin = Admin(uid=uid, username=username, password=encrypted)
            session.add(admin)
            data = RespData(code=200, message="注册成功", data={"uid": uid}).to_json()
            return MyResponse(response=data)


class LoginApi(BaseMethodView):
    def post(self):
        """
        登录
        """
        params = request.form
        username = params.get("username")
        password = params.get("password")

        with session_scope() as session:
            ua = session.query(Admin).filter(Admin.username == username).first()
            if ua is None:
                data = RespData(code=400, message="用户名或密码错误").to_json()
                return MyResponse(response=data)

        uid = ua.uid
        correct = ua.password

        salt = helper.salt_from_uid(uid)
        encrypted = helper.encrypt_password(password, salt)

        if encrypted != correct:
            data = RespData(code=400, message="用户名或密码错误").to_json()
            return MyResponse(response=data)

        token = helper.random_token()
        expires_in = Config["token_expires_in_ms"]
        db.RedisCache.set(name=token, value=uid, ex=expires_in // 1000)

        data = RespData(code=200, message="登录成功",
                        data={"uid": uid, "access_token": token, "token_type": "Bearer",
                              "expires_in": expires_in}).to_json()
        return MyResponse(response=data)


class LogoutApi(BaseMethodView):

    @helper.login_required
    def post(self, uid=None, access_token=None):
        """
        退出登录
        """
        db.RedisCache.delete(access_token)
        data = RespData(code=200, message="登出成功").to_json()
        return MyResponse(response=data)
