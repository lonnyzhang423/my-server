from sqlalchemy import Column, SmallInteger, Integer, BigInteger, String, Numeric

from database import db

__all__ = ["User", "UserAuth", "Oauth", "UserLocation", "Movie"]


class User(db.Model):
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


class UserAuth(db.Model):
    __tablename__ = "user_auth"

    id = Column(BigInteger, primary_key=True)
    uid = Column(String(128), comment="用户唯一id")
    register_type = Column(String(64), comment="注册类型")
    username = Column(String(128), comment="用户名")
    password = Column(String(128), comment="用户密码")
    verified = Column(SmallInteger, default=0, comment="是否认证过")

    def __repr__(self):
        return "UserAuth(uid={},username={})".format(self.uid, self.username)


class Oauth(db.Model):
    __tablename__ = "oauth"

    id = Column(BigInteger, primary_key=True)
    uid = Column(String(128), comment="用户唯一id")
    app_id = Column(String(128), comment="授权id")
    app_secret = Column(String(128), comment="授权secret")

    def __repr__(self):
        return "Oauth(uid={},app_id={})".format(self.uid, self.app_id)


class UserLocation(db.Model):
    __tablename__ = "user_location"

    id = Column(BigInteger, primary_key=True)
    uid = Column(String(128), comment="用户唯一id")
    longitude = Column(Numeric(11, 8), comment="经度")
    latitude = Column(Numeric(10, 8), comment="纬度")
    timestamp = Column(BigInteger, comment="时间戳")

    def __repr__(self):
        return "UserLocation(uid={},longitude={},latitude={})".format(self.uid, self.longitude, self.latitude)


class Movie(db.Model):
    __tablename__ = "movie_top250"

    id = Column(BigInteger, primary_key=True)
    title = Column(String(128), comment="中文名称")
    original_title = Column(String(128), comment="原名")
    directors = Column(String(128), comment="导演")
    casts = Column(String(128), comment="主演")
    year = Column(String(32), comment="年代")
    genres = Column(String(32), comment="类别")
    image = Column(String(128), comment="封面地址")
    rating = Column(Numeric(3, 1), comment="评分")

    def __init__(self, title, original_title, directors, casts, year, genres, image, rating):
        self.title = title
        self.original_title = original_title
        self.directors = directors
        self.casts = casts
        self.year = year
        self.genres = genres
        self.image = image
        self.rating = rating

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "original_title": self.original_title,
            "directors": self.directors,
            "casts": self.casts,
            "year": self.year,
            "image": self.image,
            "rating": self.rating,
            "genres": self.genres
        }

    def __repr__(self):
        return "Movie(id={},title={})".format(self.id, self.title)
