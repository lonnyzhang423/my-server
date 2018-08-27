import decimal
import json

from flask import Response
from flask.views import MethodView

import helper

__all__ = ["BaseMethodView", "AppResponse", "RespData"]


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
        if self.data is not None:
            d["data"] = self.data
        if self.message is not None:
            d["message"] = self.message
        return d

    def to_json(self):
        return json.dumps(self.to_dict(), cls=DecimalEncoder)

    def __repr__(self):
        return str(self.to_dict())


class AppResponse(Response):
    default_mimetype = "application/json"


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)
