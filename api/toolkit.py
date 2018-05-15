import uuid

from flask import request, Response

from api import *

__all__ = ["IPApi", "UUIDApi", "HeadersApi", "AnythingApi"]


class IPApi(BaseMethodView):

    def get(self):
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        data = RespData(code=200, data={"ip": ip}).to_json()
        return Response(response=data)


class UUIDApi(BaseMethodView):
    def get(self):
        data = RespData(code=200, data={"uuid": str(uuid.uuid4())}).to_json()
        return Response(response=data)


class HeadersApi(BaseMethodView):
    def get(self):
        headers = dict(request.headers.items())
        data = RespData(code=200, data=headers).to_json()
        return Response(response=data)


class AnythingApi(BaseMethodView):

    def get(self):
        return self.handle()

    def post(self):
        return self.handle()

    def put(self):
        return self.handle()

    def delete(self):
        return self.handle()

    def patch(self):
        return self.handle()

    def trace(self):
        return self.handle()

    @staticmethod
    def handle():
        url = request.url
        req_headers = dict(request.headers.items())
        origin = request.headers.get('X-Forwarded-For', request.remote_addr)
        method = request.method
        params = request.values.to_dict()
        resp = Response()
        resp_headers = dict(resp.headers.items())
        data = RespData(code=200, data={
            "url": url,
            "origin": origin,
            "method": method,
            "req_headers": req_headers,
            "req_data": params,
            "resp_status": resp.status,
            "resp_headers": resp_headers
        }).to_json()
        resp.response = data
        return resp
