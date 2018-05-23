from flask import request

import helper
from api import *
from db.database import session_scope
from db.models import UserLocation

__all__ = ["LocationApi", ]


class LocationApi(BaseMethodView):

    @helper.login_required
    def post(self, uid=None, access_token=None):
        params = request.form
        client_uid = params.get("uid")

        ts = int(params.get("timestamp"))
        try:
            lng = float(params.get("longitude"))
            lat = float(params.get("latitude"))
        except ValueError:
            data = RespData(code=400, message="illegal longitude or latitude").to_json()
            return MyResponse(response=data)

        if not client_uid:
            data = RespData(code=400, message="uid required").to_json()
            return MyResponse(response=data)

        if not uid:
            data = RespData(code=401, message="access_token is invalid or out of date").to_json()
            return MyResponse(status=401, response=data)

        if uid != client_uid:
            data = RespData(code=400, message="uid mismatch").to_json()
            return MyResponse(response=data)

        with session_scope() as session:
            ul = UserLocation()
            ul.uid = uid
            ul.latitude = lat
            ul.longitude = lng
            ul.timestamp = ts
            session.add(ul)

        data = RespData(code=200, message="success").to_json()
        return MyResponse(response=data)
