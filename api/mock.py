import hashlib
import hmac
import uuid

import requests

import helper
from database import db, session_scope
from database.models import Movie

host = "http://localhost:5000"


def common_params(method=None, path=None, app_id="root_app_id", app_secret="root_app_secret"):
    ts = str(helper.timestamp())
    nonce = str(uuid.uuid4())
    msg = (method + path + "?app_id=" + app_id + "&nonce=" + nonce + "&timestamp=" + ts).encode("utf8")
    app_secret = app_secret.encode("utf8")
    sig = hmac.new(app_secret, msg, hashlib.sha256).hexdigest()
    return {"timestamp": str(ts), "app_id": app_id, "nonce": nonce, "signature": sig}


def register():
    path = "/api/register"
    url = host + path
    params = common_params("POST", path)
    params["register_type"] = "phone"
    params["username"] = "18899910000"
    params["password"] = "password"
    resp = requests.post(url, data=params, timeout=3).json()
    print(resp)


def login():
    path = "/api/login"
    url = host + path
    params = common_params("POST", path)
    params["login_type"] = "phone"
    params["username"] = "18899990000"
    params["password"] = "password"
    resp = requests.post(url, data=params).json()
    print(resp)


def update_self():
    path = "/api/self"
    url = host + path
    params = common_params("PUT", path)
    params["uid"] = "751069bc779440f190fd20c6b2cde3cd"
    params["nickname"] = "foo_user"
    params["gender"] = 1
    params["headline"] = "this is headline"
    headers = {"Authorization": "Bearer 0bd028f0-6e36-493b-9d44-776522d2b444"}
    resp = requests.put(url, headers=headers, data=params).json()
    print(resp)


def get_self():
    path = "/api/self"
    url = host + path + "?"
    params = common_params("GET", path)
    params["uid"] = "751069bc779440f190fd20c6b2cde3cd"
    for k, v in params.items():
        url += k + "=" + v + "&"
    url = url[:-1]
    print(url)
    headers = {"Authorization": "Bearer 0bd028f0-6e36-493b-9d44-776522d2b444"}
    resp = requests.get(url, headers=headers).json()
    print(resp)


def get_headers():
    path = "/api/open/anything"
    url = host + path
    resp = requests.get(url).json()
    print(resp)


def get_movies():
    path = "/api/open/movies"
    url = host + path
    resp = requests.get(url).json()
    print(resp)


def post_location():
    path = "/api/user/751069bc779440f190fd20c6b2cde3cd/location"
    path.isdigit()
    url = host + path
    params = common_params("POST", path)
    params["uid"] = "751069bc779440f190fd20c6b2cde3cd"
    params["longitude"] = "123.1231231231"
    params["latitude"] = "23.11111111"
    headers = {"Authorization": "Bearer afcd8d2e-9b3d-492a-a7ac-23a13986ff2a"}
    resp = requests.post(url, data=params, headers=headers).json()
    print(resp)


def insert_movie():
    db.init_tables()

    def compose_movie(item):
        title = item["title"]
        original_title = item["original_title"]
        directors = ",".join([d["name"] for d in item["directors"]])
        casts = ",".join([c["name"] for c in item["casts"]])
        year = item["year"]
        genres = ",".join(item["genres"])
        image = item["images"]["small"]
        rating = item["rating"]["average"]
        return Movie(title, original_title, directors, casts, year, genres, image, rating)

    offset = 0
    count = 20
    while offset < 250:
        url = "https://api.douban.com/v2/movie/top250?start={}&count={}".format(offset, count)
        print(url)
        resp = requests.get(url).json()
        for item in resp["subjects"]:
            m = compose_movie(item)
            with session_scope() as session:
                session.add(m)
        offset += count


if __name__ == '__main__':
    login()
