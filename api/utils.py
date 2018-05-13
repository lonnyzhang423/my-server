import uuid

from flask import request

from api import BaseMethodView
from db.models import Response

__all__ = ["IPApi", "UUIDApi", "HeadersApi", "AnythingApi"]


class IPApi(BaseMethodView):

    def get(self):
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        return Response(code=0, data={"ip": ip}).to_json()


class UUIDApi(BaseMethodView):
    def get(self):
        return Response(code=0, data={"uuid": str(uuid.uuid4())}).to_json()


class HeadersApi(BaseMethodView):
    def get(self):
        headers = dict(request.headers.items())
        return Response(code=0, data=headers).to_json()


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
        headers = dict(request.headers.items())
        origin = request.headers.get('X-Forwarded-For', request.remote_addr)
        method = request.method
        params = request.values
        return Response(code=0, data={
            "url": url,
            "headers": headers,
            "origin": origin,
            "method": method,
            "params": params
        }).to_json()
