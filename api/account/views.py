from flask import request

import helper
from api import *
from db import db, session
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
        params = request.get_json(silent=True) if request.is_json else request.form
        if params is None:
            data = RespData(code=400, message="json参数解析异常").to_json()
            return AppResponse(response=data)

        rt = params.get("register_type")
        username = params.get("username")
        password = params.get("password")

        if rt not in self.RT:
            if rt is None:
                data = RespData(code=400, message="缺少注册类型").to_json()
            else:
                data = RespData(code=400, message="不支持:{}注册类型".format(rt)).to_json()
            return AppResponse(response=data)

        if not helper.check_phone_num(username):
            data = RespData(code=400, message="手机号不合法").to_json()
            return AppResponse(response=data)

        if not helper.check_password(password):
            data = RespData(code=400, message="密码不合法").to_json()
            return AppResponse(response=data)

        with session() as sess:
            ua = sess.query(UserAuth).filter(UserAuth.username == username).first()
            if ua:
                data = RespData(code=400, message="用户名:{}已存在".format(username)).to_json()
                return AppResponse(response=data)

            uid = helper.random_uid()
            salt = helper.salt_from_uid(uid)
            encrypted = helper.encrypt_password(password, salt)

            user = User(uid=uid)
            user_auth = UserAuth(uid=uid, register_type=rt, username=username, password=encrypted)
            sess.add(user)
            sess.add(user_auth)
        data = RespData(code=200, message="注册成功", data={"uid": uid}).to_json()
        return AppResponse(response=data)


class LoginApi(BaseMethodView):
    def post(self):
        """
        登录
        """
        params = request.get_json(silent=True) if request.is_json else request.form
        if params is None:
            data = RespData(code=400, message="json参数解析异常").to_json()
            return AppResponse(response=data)

        gt = params.get("login_type")
        username = params.get("username")
        password = params.get("password")

        if gt not in RegisterApi.RT:
            if gt is None:
                data = RespData(code=400, message="缺少注册类型").to_json()
            else:
                data = RespData(code=400, message="不支持:{}注册类型}".format(gt)).to_json()
            return AppResponse(response=data)

        if not helper.check_phone_num(username):
            data = RespData(code=400, message="手机号不合法").to_json()
            return AppResponse(response=data)

        if not helper.check_password(password):
            data = RespData(code=400, message="密码不合法").to_json()
            return AppResponse(response=data)

        with session() as sess:
            ua = sess.query(UserAuth).filter(UserAuth.username == username).first()
            if ua is None:
                data = RespData(code=400, message="用户名或密码错误").to_json()
                return AppResponse(response=data)

        uid = ua.uid
        correct = ua.password

        salt = helper.salt_from_uid(uid)
        encrypted = helper.encrypt_password(password, salt)

        if encrypted != correct:
            data = RespData(code=400, message="用户名或密码错误").to_json()
            return AppResponse(response=data)

        token = helper.random_token()
        expires_in = 30 * 24 * 60 * 60 * 1000
        db.Redis.set(name=token, value=uid, ex=expires_in // 1000)

        data = RespData(code=200, message="登录成功",
                        data={"uid": uid, "access_token": token, "token_type": "Bearer",
                              "expires_in": expires_in}).to_json()
        return AppResponse(response=data)


class LogoutApi(BaseMethodView):
    @helper.login_required
    def post(self, uid=None, access_token=None):
        """
        退出登录
        """
        db.Redis.delete(access_token)
        data = RespData(code=200, message="登出成功").to_json()
        return AppResponse(response=data)


# noinspection PyMethodMayBeStatic
class SelfApi(BaseMethodView):
    @helper.login_required
    def get(self, uid=None, access_token=None):
        """
        获取个人信息
        """
        with session() as sess:
            target = sess.query(User).filter(User.uid == uid).first()
            if target:
                data = RespData(code=200, message="成功", data=target.to_dict()).to_json()
                return AppResponse(response=data)
            else:
                data = RespData(code=400, message="未获取到用户信息").to_json()
                return AppResponse(response=data)

    @helper.login_required
    def put(self, uid=None, access_token=None):
        """
        更新个人信息
        """
        params = request.get_json(silent=True) if request.is_json else request.form
        if params is None:
            data = RespData(code=400, message="json参数解析异常").to_json()
            return AppResponse(response=data)
        nickname = params.get("nickname")
        gender = params.get("gender")
        headline = params.get("headline")

        with session() as sess:
            target = sess.query(User).filter(User.uid == uid).first()
            if target:
                target.nickname = nickname
                target.gender = gender
                target.headline = headline
                data = RespData(code=200, message="更新成功", data=target.to_dict()).to_json()
                return AppResponse(response=data)
            else:
                data = RespData(code=400, message="更新失败：未查询到用户信息").to_json()
                return AppResponse(response=data)


class PasswordApi(BaseMethodView):
    def put(self):
        pass
