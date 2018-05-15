import json

import helper
from flask import Response
from flask.views import MethodView

__all__ = ["BaseMethodView", "RespData"]


class BaseMethodView(MethodView):

    # noinspection PyBroadException
    def dispatch_request(self, *args, **kwargs):
        try:
            return super().dispatch_request(*args, **kwargs)
        except BaseException:
            helper.logger.fatal("Caught Unhandled Exception.", exc_info=True)
            data = RespData(code=500, message="Internal Server Error").to_json()
            return Response(status=500, response=data)


class RespData:
    def __init__(self, code=200, message=None, data=None):
        self.code = code
        self.data = data
        self.message = message

    def to_dict(self):
        d = {"code": self.code}
        if self.data:
            d["data"] = self.data
        if self.message:
            d["message"] = self.message
        return d

    def to_json(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())
