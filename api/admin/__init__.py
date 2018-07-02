from flask import Blueprint

from api.admin.views import *
from config import Config

__all__ = ["admin", ]

admin = Blueprint("admin", __name__)

if Config.get("debug", False):
    # disable admin register api in production environment
    admin.add_url_rule("/register", view_func=RegisterApi.as_view("register"))

admin.add_url_rule("/login", view_func=LoginApi.as_view("login"))
admin.add_url_rule("/logout", view_func=LogoutApi.as_view("logout"))
