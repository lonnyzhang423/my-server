from flask import Blueprint

from api.account.views import *

__all__ = ["account", ]

account = Blueprint("account", __name__)

account.add_url_rule("/register", view_func=RegisterApi.as_view("register"))
account.add_url_rule("/login", view_func=LoginApi.as_view("login"))
account.add_url_rule("/logout", view_func=LogoutApi.as_view("logout"))
account.add_url_rule("/self", view_func=SelfApi.as_view("self"))
