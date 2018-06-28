from flask import Blueprint

from api.location.views import LocationApi

__all__ = ["location", ]

location = Blueprint("location", __name__)
location.add_url_rule("/location", view_func=LocationApi.as_view("location"))
