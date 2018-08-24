import datetime

from flask import request

import helper
from api import *
from db import session
from db.models import BlogArticle

__all__ = ["BlogArticleApi", "BlogArticleDetailApi"]


class BlogArticleApi(BaseMethodView):

    def get(self, uid=None, access_token=None):
        params = request.args

        try:
            offset = min(int(params.get("offset", 0)), 1000)
            limit = min(int(params.get("limit", 10)), 20)
        except ValueError:
            data = RespData(400, message="参数不合法").to_json()
            return MyResponse(response=data)

        with session() as sess:
            query = sess.query(BlogArticle).offset(offset).limit(limit)
            articles = [article.to_dict() for article in query]
            data = RespData(code=200, message="成功", data=articles).to_json()
            return MyResponse(response=data)

    # noinspection PyBroadException
    @helper.admin_login_required
    def post(self, uid=None, access_token=None):
        params = request.get_json(silent=True) if request.is_json else request.form

        title = params.get("title")
        content = params.get("content")
        create_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not title or not content:
            data = RespData(400, message="参数不合法").to_json()
            return MyResponse(response=data)

        with session() as sess:
            article = BlogArticle()
            article.title = title
            article.content = content
            article.create_at = create_at
            sess.add(article)
            data = RespData(code=200, message="成功").to_json()
            return MyResponse(response=data)


class BlogArticleDetailApi(BaseMethodView):

    def get(self, aid=None, uid=None, access_token=None):
        if not aid:
            data = RespData(400, message="文章id为空").to_json()
            return MyResponse(response=data)
        with session() as sess:
            article = sess.query(BlogArticle).filter(BlogArticle.id == aid).first()
            if article:
                data = RespData(200, message="成功", data=article.to_dict()).to_json()
            else:
                data = RespData(400, message="文章id不存在").to_json()
            return MyResponse(response=data)

    @helper.admin_login_required
    def put(self, aid=None, uid=None, access_token=None):

        params = request.get_json(silent=True) if request.is_json else request.form
        if params is None:
            data = RespData(code=400, message="json参数解析异常").to_json()
            return MyResponse(response=data)

        if not aid:
            data = RespData(400, message="文章id为空").to_json()
            return MyResponse(response=data)

        title = params.get("title")
        content = params.get("content")
        update_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with session() as sess:
            article = sess.query(BlogArticle).filter(BlogArticle.id == aid).first()
            if article:
                article.title = title
                article.content = content
                article.update_at = update_at
                data = RespData(200, message="成功").to_json()
            else:
                data = RespData(400, message="文章id不存在").to_json()
        return MyResponse(response=data)

    @helper.admin_login_required
    def delete(self, aid=None, uid=None, access_token=None):

        if not aid:
            data = RespData(400, message="文章id为空").to_json()
            return MyResponse(response=data)

        with session() as sess:
            article = sess.query(BlogArticle).filter(BlogArticle.id == aid).first()
            if article:
                sess.delete(article)
                data = RespData(200, message="删除成功").to_json()
            else:
                data = RespData(400, message="文章id不存在").to_json()
            return MyResponse(response=data)
