from flask import Blueprint

from open.views import *

__all__ = ["toolkit", ]

toolkit = Blueprint("open", __name__)

toolkit.add_url_rule("/ip", view_func=IPApi.as_view("ip"))
toolkit.add_url_rule("/headers", view_func=HeadersApi.as_view("headers"))
toolkit.add_url_rule("/uuid", view_func=UUIDApi.as_view("uuid"))
toolkit.add_url_rule("/anything", view_func=AnythingApi.as_view("anything"))
toolkit.add_url_rule("/captcha", view_func=CaptchaApi.as_view("captcha"))
toolkit.add_url_rule("/movies", view_func=MovieApi.as_view("movie"))
