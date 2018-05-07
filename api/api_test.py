import hashlib
import hmac

import requests

from api.utils import timestamp

host = "http://localhost:5000"


def common_params(method=None, path=None, app_id="app_id", app_secret="app_secret"):
    ts = timestamp()
    msg = (method + path + "?app_id=" + app_id + "&timestamp=" + str(ts)).encode("utf8")
    app_secret = app_secret.encode("utf8")
    sig = hmac.new(app_secret, msg, hashlib.sha1).hexdigest()
    return {"timestamp": str(ts), "app_id": app_id, "signature": sig}


def register():
    path = "/api/register"
    url = host + path
    params = common_params("POST", path)
    params["register_type"] = "phone"
    params["username"] = "18899990000"
    params["password"] = "password"
    resp = requests.post(url, data=params).json()
    print(resp)


def login():
    path = "/api/login"
    url = host + path
    params = common_params("POST", path)
    params["login_type"] = "phone"
    params["username"] = "12345678971"
    params["password"] = "password"
    resp = requests.post(url, data=params).json()
    print(resp)


def self():
    path = "/api/self"
    url = host + path + "?"
    params = common_params("GET", path)
    params["uid"] = "6867ebca9afd48a09c0dbed86b449358"
    for k, v in params.items():
        url += k + "=" + v + "&"
    url = url[:-1]
    print(url)
    headers = {"Authorization": "Bearer bd7d2226-691a-4f0b-91ad-5941842bd329"}
    resp = requests.get(url, headers=headers).json()
    print(resp)


if __name__ == '__main__':
    register()
    login()
    self()
