from flask import request

import helper
from api import *
from database import session_scope
from database.models import UserLocation

__all__ = ["LocationApi", ]


class LocationApi(BaseMethodView):

    @helper.login_required
    def post(self, uid=None, access_token=None):
        params = request.form

        try:
            ts = int(params.get("timestamp"))
            lng = float(params.get("longitude"))
            lat = float(params.get("latitude"))
        except ValueError:
            data = RespData(code=400, message="经纬度不合法").to_json()
            return MyResponse(response=data)

        with session_scope() as session:
            ul = UserLocation()
            ul.uid = uid
            ul.latitude = lat
            ul.longitude = lng
            ul.timestamp = ts
            session.add(ul)

        data = RespData(code=200, message="成功").to_json()
        return MyResponse(response=data)

    @helper.login_required
    def get(self, uid=None, access_token=None):
        with session_scope() as session:
            result = session.query(UserLocation).filter(UserLocation.uid == uid)
            result = [ul for ul in result]
            data = RespData(code=200, message="成功", data=result).to_json()
            return MyResponse(response=data)
