from flask import Blueprint

from api.open.views import *

__all__ = ["openapi", ]

openapi = Blueprint("open", __name__)

openapi.add_url_rule("/ip", view_func=IPApi.as_view("ip"))
openapi.add_url_rule("/headers", view_func=HeadersApi.as_view("headers"))
openapi.add_url_rule("/uuid", view_func=UUIDApi.as_view("uuid"))
openapi.add_url_rule("/anything", view_func=AnythingApi.as_view("anything"))
openapi.add_url_rule("/movies", view_func=MovieApi.as_view("movie"))
openapi.add_url_rule("/captcha", view_func=CaptchaApi.as_view("captcha"))
