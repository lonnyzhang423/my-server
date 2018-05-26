from flask import Blueprint

from toolkit.views import *

__all__ = ["toolkit", ]

toolkit = Blueprint("toolkit", __name__)

toolkit.add_url_rule("/ip", view_func=IPApi.as_view("ip"))
toolkit.add_url_rule("/headers", view_func=HeadersApi.as_view("headers"))
toolkit.add_url_rule("/uuid", view_func=UUIDApi.as_view("uuid"))
toolkit.add_url_rule("/anything", view_func=AnythingApi.as_view("anything"))
