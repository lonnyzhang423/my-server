from flask import request
from flask.views import MethodView

import utils
from config import Config
from db.database import RedisCache, session_scope
from db.models import *

__all__ = ["RegisterApi", "LoginApi", "LogoutApi", "SelfApi", "PasswordApi"]


class BaseMethodView(MethodView):

    # noinspection PyBroadException
    def dispatch_request(self, *args, **kwargs):
        try:
            return super().dispatch_request(*args, **kwargs)
        except BaseException:
            return Response.e_500().to_json(), 500


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
                return Response(code=400, message="register_type required").to_json(), 400
            else:
                return Response(code=400, message="unsupported register_type:{}".format(rt)).to_json(), 400

        if not utils.valid_phone(username):
            return Response(400, message="illegal phone num").to_json(), 400

        if not utils.valid_password(password):
            return Response(400, message="illegal password").to_json(), 400

        with session_scope() as session:
            ua = session.query(UserAuth).filter(UserAuth.username == username).first()
            if ua:
                return Response(400, message="username:{} already exists".format(username)).to_json(), 400

            uid = utils.random_uid()
            salt = utils.salt_from_uid(uid)
            encrypted_password = UserAuth.encrypt_password(password, salt)

            user = User(uid=uid)
            user_auth = UserAuth(uid=uid, register_type=rt, username=username, password=encrypted_password)
            session.add(user)
            session.add(user_auth)

        return Response(code=0, message="register success", data={"uid": uid}).to_json()


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
                return Response(code=400, message="login_type required").to_json(), 400
            else:
                return Response(code=400, message="unsupported login_type:{}".format(gt)).to_json(), 400

        if not utils.valid_phone(username):
            return Response(400, message="illegal phone num").to_json(), 400

        if not utils.valid_password(password):
            return Response(400, message="illegal password").to_json(), 400

        with session_scope() as session:
            ua = session.query(UserAuth).filter(UserAuth.username == username).first()
            if ua is None:
                return Response(code=400, message="username or password is wrong").to_json(), 400

        uid = ua.uid
        correct = ua.password

        salt = utils.salt_from_uid(uid)
        encrypted = UserAuth.encrypt_password(password, salt)

        if encrypted != correct:
            return Response(code=400, message="username or password is wrong").to_json(), 400

        token = utils.random_token()
        expires_in = Config["token_expires_in_ms"]
        RedisCache.set(name=token, value=uid, ex=expires_in // 1000)

        return Response(code=0, message="login success",
                        data={"uid": uid, "access_token": token, "token_type": "Bearer",
                              "expires_in": expires_in}).to_json()


class LogoutApi(BaseMethodView):

    @utils.login_required
    def post(self, uid=None, access_token=None):
        """
        退出登录
        """
        params = request.form
        client_uid = params.get("uid")
        if not client_uid:
            return Response(400, "uid required").to_json(), 400
        if client_uid != uid:
            return Response(400, "uid mismatch").to_json(), 400
        RedisCache.delete(access_token)
        return Response(0, message="logout success uid:{}".format(uid)).to_json()


# noinspection PyMethodMayBeStatic
class SelfApi(BaseMethodView):

    @utils.login_required
    def get(self, uid: object = None, access_token: object = None) -> object:
        """
        获取个人信息
        """
        params = request.args
        client_uid = params.get("uid")

        if not client_uid:
            return Response(400, "uid required").to_json(), 400

        if uid != client_uid:
            return Response(400, "uid mismatch").to_json(), 400

        with session_scope() as session:
            target = session.query(User).filter(User.uid == uid).first()
            if target:
                return Response(0, data=target.to_dict()).to_json()
            else:
                return Response.e_500().to_json(), 500

    @utils.login_required
    def put(self, uid=None, access_token=None):
        """
        更新个人信息
        """
        params = request.form
        client_uid = params.get("uid")
        nickname = params.get("nickname")
        gender = params.get("gender")
        headline = params.get("headline")

        if not client_uid:
            return Response(400, "uid required").to_json(), 400

        if not uid:
            return Response(401, "access_token is invalid or out of date").to_json(), 401

        if uid != client_uid:
            return Response(401, "uid mismatch").to_json(), 400

        with session_scope() as session:
            target = session.query(User).filter(User.uid == uid).first()
            if target:
                target.nickname = nickname
                target.gender = gender
                target.headline = headline
                return Response(0, message="update success", data=target.to_dict()).to_json()
            else:
                return Response(500, "uid not found").to_json(), 500


class PasswordApi(BaseMethodView):

    def put(self):
        pass
