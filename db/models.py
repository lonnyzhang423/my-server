import hashlib
import hmac

from sqlalchemy import Column, SmallInteger, Integer, BigInteger, String

from db.database import Model

__all__ = ["User", "UserAuth", "Oauth"]


class User(Model):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    uid = Column(String(128), comment="用户唯一id")
    nickname = Column(String(128), comment="昵称")
    gender = Column(SmallInteger, comment="性别，0:女 1:男")
    avatar = Column(String(128), comment="头像地址")
    birthday = Column(Integer, comment="生日")
    headline = Column(String(256), comment="简介")

    def to_dict(self):
        result = {"uid": self.uid}

        if self.nickname:
            result["nickname"] = self.nickname
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
        return "User(uid={},name={})".format(self.uid, self.nickname)


class UserAuth(Model):
    __tablename__ = "user_auth"

    id = Column(BigInteger, primary_key=True)
    uid = Column(String(128), comment="用户唯一id")
    register_type = Column(String(64), comment="注册类型")
    username = Column(String(128), comment="用户名")
    password = Column(String(128), comment="用户密码")
    verified = Column(SmallInteger, default=0, comment="是否认证过")

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
    def __repr__(self):
        return "Oauth(uid={},app_id={})".format(self.uid, self.app_id)
