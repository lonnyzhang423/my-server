import hashlib
import hmac

from flask import jsonify
from sqlalchemy import Column, SmallInteger, Integer, BigInteger, String

from db.database import Model, session_scope

__all__ = ["User", "UserAuth", "Response", "Oauth"]


class User(Model):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    uid = Column(String(128), comment="用户唯一id")
    nick_name = Column(String(128), comment="昵称")
    gender = Column(SmallInteger, comment="性别，0:女 1:男")
    avatar = Column(String(128), comment="头像地址")
    birthday = Column(Integer, comment="生日")
    headline = Column(String(256), comment="简介")

    def to_json(self):
        return jsonify(self.to_dict())

    def to_dict(self):
        result = {"uid": self.uid}

        if self.nick_name:
            result["nick_name"] = self.nick_name
        if self.gender:
            result["gender"] = self.gender
        if self.avatar:
            result["avatar"] = self.avatar
        if self.birthday:
            result["birthday"] = self.birthday
        if self.headline:
            result["headline"] = self.headline
        return result

    def __repr__(self):
        return "User(uid={},name={})".format(self.uid, self.nick_name)


class UserAuth(Model):
    __tablename__ = "user_auth"

    id = Column(BigInteger, primary_key=True)
    uid = Column(String(128), comment="用户唯一id")
    register_type = Column(String(64), comment="注册类型")
    username = Column(String(128), comment="用户名")
    password = Column(String(128), comment="用户密码")
    verified = Column(SmallInteger, default=0, comment="是否认证过")

    @staticmethod
    def search(username):
        with session_scope() as session:
            target = session.query(UserAuth).filter(UserAuth.username == username).first()
        return target

    @staticmethod
    def encrypt_password(password, salt):
        if isinstance(password, str):
            password = password.encode("utf8")
        if isinstance(salt, str):
            salt = salt.encode("utf8")
        return hmac.new(salt, password, hashlib.sha256).hexdigest()

    def __repr__(self):
        return "UserAuth(uid={},username={})".format(self.uid, self.username)


class Oauth(Model):
    __tablename__ = "oauth"

    id = Column(BigInteger, primary_key=True)
    uid = Column(String(128), comment="用户唯一id")
    app_id = Column(String(128), comment="授权id")
    app_secret = Column(String(128), comment="授权secret")

    @staticmethod
    def search(app_id):
        with session_scope() as sess:
            target = sess.query(Oauth).filter(Oauth.app_id == app_id).first()
        return target

    @staticmethod
    def __repr__(self):
        return "Oauth(uid={},app_id={})".format(self.uid, self.app_id)


class Response(object):

    def __init__(self, code=0, message=None, data=None):
        self.code = code
        self.data = data
        self.message = message

    def to_dict(self):
        d = {"code": self.code}
        if self.data:
            d["data"] = self.data
        if self.message:
            d["message"] = self.message
        return d

    def to_json(self):
        return jsonify(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())

    @staticmethod
    def e_400():
        return Response(400, "Bad Request")

    @staticmethod
    def e_401():
        return Response(401, "Unauthorized")

    @staticmethod
    def e_403():
        return Response(403, "Forbidden")

    @staticmethod
    def e_404():
        return Response(404, "Not Found")

    @staticmethod
    def e_405():
        return Response(405, "Method Not Allowed")

    @staticmethod
    def e_500():
        return Response(500, "Internal Server Error")

    @staticmethod
    def e_503():
        return Response(503, "Service Unavailable")

    @staticmethod
    def e_505():
        return Response(505, "HTTP Version Not Supported")
