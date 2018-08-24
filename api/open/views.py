import uuid

from flask import request

from api import BaseMethodView, RespData, MyResponse
from config import Config
from db import session
from db.models import Movie, Mock

__all__ = ["IPApi", "UUIDApi", "HeadersApi", "AnythingApi", "CaptchaApi",
           "MovieApi", "MockApi", "MockDynamicApi"]


class IPApi(BaseMethodView):
    def get(self):
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        data = RespData(code=200, message="success", data={"ip": ip}).to_json()
        return MyResponse(response=data)


class UUIDApi(BaseMethodView):
    def get(self):
        data = RespData(code=200, message="success", data={"uuid": str(uuid.uuid4())}).to_json()
        return MyResponse(response=data)


class HeadersApi(BaseMethodView):
    def get(self):
        headers = dict(request.headers.items())
        data = RespData(code=200, message="success", data=headers).to_json()
        return MyResponse(response=data)


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

        resp = MyResponse()
        resp_headers = dict(resp.headers.items())
        data = RespData(code=200, message="success",
                        data={"url": url,
                              "origin": origin,
                              "method": method,
                              "req_headers": req_headers,
                              "req_data": params,
                              "resp_status": resp.status,
                              "resp_headers": resp_headers}).to_json()
        resp.data = data
        return resp


class CaptchaApi(BaseMethodView):
    def post(self):
        # lazy load captcha api
        # todo: speed up
        from api.open.captcha import predict_captcha
        from api.open.captcha.config import INVALID_CAPTCHA

        args = request.get_json(silent=True) if request.is_json else request.form
        img = args.get("img_base64", "")
        if not img:
            data = RespData(code=400, message="img_base64 required").to_json()
            return MyResponse(response=data)

        text = predict_captcha(img)
        if text == INVALID_CAPTCHA:
            data = RespData(code=400, message="illegal img_base64").to_json()
        else:
            data = RespData(code=200, message="success", data={"predict": text}).to_json()
        return MyResponse(response=data)


class MovieApi(BaseMethodView):
    def get(self):
        args = request.args
        offset = min(int(args.get("offset", 0)), 1000)
        limit = min(int(args.get("limit", 20)), 40)

        with session() as sess:
            query = sess.query(Movie).limit(limit).offset(offset)
            movies = [movie.to_dict() for movie in query]
            data = RespData(code=200, message="success", data=movies).to_json()
            return MyResponse(response=data)


class MockApi(BaseMethodView):
    def post(self):
        args = request.get_json(silent=True) if request.is_json else request.form
        secret = args.get("secret", "")
        path = args.get("path", "")
        content = args.get("content", "")
        if secret != Config["mock_secret"]:
            data = RespData(code=400, message="illegal secret").to_json()
            return MyResponse(response=data)
        if not path or not content:
            data = RespData(code=400, message="illegal arguments").to_json()
            return MyResponse(response=data)

        with session() as sess:
            mock = sess.query(Mock).filter(Mock.path == path).first()
            if not mock:
                mock = Mock()
            mock.path = path
            mock.content = content
            sess.add(mock)
            data = RespData(code=200, message="success").to_json()
            return MyResponse(response=data)


class MockDynamicApi(BaseMethodView):
    def get(self, path=None):
        if not path:
            data = RespData(code=400, message="illegal path").to_json()
            return MyResponse(response=data)
        with session() as sess:
            mock = sess.query(Mock).filter(Mock.path == path).first()
            if not mock:
                data = RespData(code=400, message="path doesn't exists").to_json()
            else:
                data = mock.content
            return MyResponse(response=data)
