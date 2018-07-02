from flask import Blueprint

from api.blog.views import BlogArticleApi, BlogArticleDetailApi

__all__ = ["blog", ]

blog = Blueprint("blog", __name__)
blog.add_url_rule("/articles", view_func=BlogArticleApi.as_view("blog_article"))
blog.add_url_rule("/articles/<aid>", view_func=BlogArticleDetailApi.as_view("blog_article_detail"))
